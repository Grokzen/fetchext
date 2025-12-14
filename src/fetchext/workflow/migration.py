import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass, field
from fetchext.core.exceptions  import ExtensionError
from fetchext.plugins.hooks  import HookManager, HookContext
from fetchext.data.config  import get_config_path, load_config

logger = logging.getLogger(__name__)


@dataclass
class MigrationReport:
    changes: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class MV3Migrator:
    """
    Migrates Manifest V2 extensions to Manifest V3.
    """

    def __init__(self, source_dir: Path):
        self.source_dir = Path(source_dir)
        self.manifest_path = self.source_dir / "manifest.json"
        self.report = MigrationReport()

    def migrate(self, dry_run: bool = False) -> MigrationReport:
        if not self.manifest_path.exists():
            raise ExtensionError(f"Manifest not found: {self.manifest_path}")

        # Initialize hooks
        config_dir = get_config_path().parent
        hooks_dir = config_dir / "hooks"
        hook_manager = HookManager(hooks_dir)
        try:
            config = load_config()
        except Exception:
            config = {}

        # Run pre-migrate hook
        ctx = HookContext(
            extension_id="unknown",
            browser="unknown",
            file_path=self.source_dir,
            config=config,
        )
        hook_manager.run_hook("pre_migrate", ctx)

        if ctx.cancel:
            logger.info("Migration cancelled by pre_migrate hook.")
            return self.report

        try:
            with open(self.manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
        except json.JSONDecodeError as e:
            raise ExtensionError(f"Invalid manifest JSON: {e}")

        if manifest.get("manifest_version") == 3:
            self.report.warnings.append("Extension is already Manifest V3.")
            return self.report

        new_manifest = manifest.copy()
        new_manifest["manifest_version"] = 3
        self.report.changes.append("Updated manifest_version to 3")

        # 1. Host Permissions
        self._migrate_permissions(new_manifest)

        # 2. Action API
        self._migrate_action(new_manifest)

        # 3. Background Scripts
        self._migrate_background(new_manifest, dry_run)

        # 4. CSP
        self._migrate_csp(new_manifest)

        # 5. Web Accessible Resources
        self._migrate_war(new_manifest)

        # Save changes
        if not dry_run:
            with open(self.manifest_path, "w", encoding="utf-8") as f:
                json.dump(new_manifest, f, indent=2)
            self.report.changes.append(
                f"Saved updated manifest to {self.manifest_path}"
            )

        # Run post-migrate hook
        ctx.result = self.report
        hook_manager.run_hook("post_migrate", ctx)

        return self.report

    def _migrate_permissions(self, manifest: Dict[str, Any]):
        permissions = manifest.get("permissions", [])
        host_permissions = []
        new_permissions = []

        for p in permissions:
            if "://" in p or p == "<all_urls>":
                host_permissions.append(p)
            else:
                new_permissions.append(p)

        if host_permissions:
            manifest["permissions"] = new_permissions
            manifest["host_permissions"] = host_permissions
            self.report.changes.append(
                f"Moved {len(host_permissions)} host permissions to 'host_permissions'"
            )

    def _migrate_action(self, manifest: Dict[str, Any]):
        action = {}

        if "browser_action" in manifest:
            action.update(manifest.pop("browser_action"))
            self.report.changes.append("Renamed 'browser_action' to 'action'")

        if "page_action" in manifest:
            action.update(manifest.pop("page_action"))
            self.report.changes.append("Renamed 'page_action' to 'action'")
            self.report.warnings.append(
                "Merged 'page_action' into 'action'. Check logic for enabling/disabling."
            )

        if action:
            manifest["action"] = action

    def _migrate_background(self, manifest: Dict[str, Any], dry_run: bool):
        bg = manifest.get("background", {})
        if "scripts" in bg:
            scripts = bg.pop("scripts")
            if not scripts:
                return

            if len(scripts) == 1:
                bg["service_worker"] = scripts[0]
                # bg["type"] = "module" # Optional, but good practice if using ES6
            else:
                # Multiple scripts need a wrapper
                wrapper_name = "background_wrapper.js"
                wrapper_content = ""
                for s in scripts:
                    wrapper_content += f"importScripts('{s}');\n"

                if not dry_run:
                    wrapper_path = self.source_dir / wrapper_name
                    try:
                        with open(wrapper_path, "w", encoding="utf-8") as f:
                            f.write(wrapper_content)
                        self.report.changes.append(
                            f"Created '{wrapper_name}' to import multiple background scripts"
                        )
                    except Exception as e:
                        self.report.errors.append(
                            f"Failed to create wrapper script: {e}"
                        )

                bg["service_worker"] = wrapper_name
                self.report.warnings.append(
                    f"Multiple background scripts found. Created '{wrapper_name}' (if not dry-run)."
                )

            if "persistent" in bg:
                del bg["persistent"]
                self.report.changes.append(
                    "Removed 'background.persistent' (Service Workers are ephemeral)"
                )

            manifest["background"] = bg
            self.report.changes.append("Converted background scripts to service_worker")

    def _migrate_csp(self, manifest: Dict[str, Any]):
        csp = manifest.get("content_security_policy")
        if isinstance(csp, str):
            # MV2 string format -> MV3 object format
            new_csp = {"extension_pages": csp}
            manifest["content_security_policy"] = new_csp
            self.report.changes.append("Converted CSP string to object format")
            self.report.warnings.append(
                "Review CSP: 'script-src' must not allow 'unsafe-eval' or remote sources."
            )

    def _migrate_war(self, manifest: Dict[str, Any]):
        war = manifest.get("web_accessible_resources")
        if war and isinstance(war, list) and len(war) > 0 and isinstance(war[0], str):
            # MV2 list of strings -> MV3 list of objects

            # Try to find matches from content_scripts
            matches = set()
            content_scripts = manifest.get("content_scripts", [])
            if isinstance(content_scripts, list):
                for script in content_scripts:
                    if isinstance(script, dict) and "matches" in script:
                        matches.update(script["matches"])

            final_matches = sorted(list(matches)) if matches else ["<all_urls>"]

            new_war = [{"resources": war, "matches": final_matches}]
            manifest["web_accessible_resources"] = new_war
            self.report.changes.append(
                "Converted web_accessible_resources to object format"
            )
