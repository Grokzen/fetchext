import re
import json
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pathlib import Path
from fetchext.utils  import open_extension_archive


@dataclass
class AuditIssue:
    severity: str  # "error", "warning", "info"
    message: str
    file: str = "manifest.json"
    line: Optional[int] = None


@dataclass
class AuditReport:
    manifest_version: int
    issues: List[AuditIssue] = field(default_factory=list)

    @property
    def is_mv3(self):
        return self.manifest_version == 3


class ExtensionAuditor:
    def audit(self, file_path: Path) -> AuditReport:
        with open_extension_archive(file_path) as zf:
            # Read manifest
            try:
                manifest_data = zf.read("manifest.json")
                manifest = json.loads(manifest_data)
            except KeyError:
                return AuditReport(0, [AuditIssue("error", "manifest.json not found")])
            except json.JSONDecodeError:
                return AuditReport(
                    0, [AuditIssue("error", "manifest.json is invalid JSON")]
                )

            report = AuditReport(manifest_version=manifest.get("manifest_version", 0))

            self._check_manifest(manifest, report)
            self._check_csp(manifest, report)
            self._scan_code(zf, report)

            return report

    def _check_manifest(self, manifest: Dict[str, Any], report: AuditReport):
        mv = report.manifest_version
        if mv == 2:
            report.issues.append(
                AuditIssue(
                    "warning", "Extension is using Manifest V2, which is deprecated."
                )
            )
        elif mv == 3:
            report.issues.append(AuditIssue("info", "Extension is using Manifest V3."))
        else:
            report.issues.append(AuditIssue("error", f"Unknown manifest version: {mv}"))

        # Check for deprecated keys in MV3 context
        # Even if it is MV2, we warn about migration

        if "browser_action" in manifest:
            report.issues.append(
                AuditIssue(
                    "warning",
                    "'browser_action' is deprecated in MV3. Use 'action' instead.",
                )
            )

        if "page_action" in manifest:
            report.issues.append(
                AuditIssue(
                    "warning",
                    "'page_action' is deprecated in MV3. Use 'action' instead.",
                )
            )

        if "background" in manifest:
            bg = manifest["background"]
            if "scripts" in bg:
                report.issues.append(
                    AuditIssue(
                        "warning",
                        "Persistent background pages ('background.scripts') are replaced by Service Workers in MV3.",
                    )
                )
            if "persistent" in bg and bg["persistent"]:
                report.issues.append(
                    AuditIssue(
                        "warning",
                        "Persistent background pages are not supported in MV3.",
                    )
                )

    def _check_csp(self, manifest: Dict[str, Any], report: AuditReport):
        """Analyze Content Security Policy for weaknesses."""
        csp = manifest.get("content_security_policy")
        if not csp:
            return

        policies = []

        # Normalize CSP to a list of strings to check
        if isinstance(csp, str):
            # MV2 format
            policies.append(("MV2 Policy", csp))
        elif isinstance(csp, dict):
            # MV3 format
            if "extension_pages" in csp:
                policies.append(("MV3 Extension Pages", csp["extension_pages"]))
            if "sandbox" in csp:
                policies.append(("MV3 Sandbox", csp["sandbox"]))

        for context, policy_str in policies:
            self._analyze_policy_string(context, policy_str, report)

    def _analyze_policy_string(self, context: str, policy: str, report: AuditReport):
        """Check a single CSP string for insecure directives."""
        # Check for unsafe-eval
        if "'unsafe-eval'" in policy:
            report.issues.append(
                AuditIssue(
                    "warning",
                    f"CSP ({context}) allows 'unsafe-eval'. This enables code execution from strings and is a security risk.",
                )
            )

        # Check for unsafe-inline (often ignored in MV3 but still bad practice)
        if "'unsafe-inline'" in policy:
            report.issues.append(
                AuditIssue(
                    "warning",
                    f"CSP ({context}) allows 'unsafe-inline'. This enables inline scripts and increases XSS risk.",
                )
            )

        # Check for insecure schemes
        if "http:" in policy:
            report.issues.append(
                AuditIssue(
                    "warning", f"CSP ({context}) allows insecure 'http:' sources."
                )
            )

        if "ftp:" in policy:
            report.issues.append(
                AuditIssue(
                    "warning", f"CSP ({context}) allows insecure 'ftp:' sources."
                )
            )

        # Check for wildcards in script-src
        # Simple heuristic: look for script-src followed by *
        # This is a bit loose but catches obvious cases
        if re.search(r"script-src[^;]*\*", policy):
            report.issues.append(
                AuditIssue(
                    "warning",
                    f"CSP ({context}) contains wildcard '*' in script-src. This allows loading scripts from any domain.",
                )
            )

    def _scan_code(self, zf, report: AuditReport):
        # Simple regex scan for JS files
        js_files = [f for f in zf.namelist() if f.endswith(".js")]

        patterns = [
            (
                r"chrome\.browserAction",
                "warning",
                "chrome.browserAction is deprecated in MV3. Use chrome.action.",
            ),
            (
                r"chrome\.pageAction",
                "warning",
                "chrome.pageAction is deprecated in MV3. Use chrome.action.",
            ),
            (
                r"chrome\.webRequest",
                "info",
                "chrome.webRequest blocking is limited in MV3. Consider declarativeNetRequest.",
            ),
        ]

        for filename in js_files:
            try:
                # Limit read size to avoid memory issues with massive JS files?
                # For now, read full.
                content = zf.read(filename).decode("utf-8", errors="ignore")
                lines = content.splitlines()
                for i, line in enumerate(lines):
                    for pattern, severity, msg in patterns:
                        if re.search(pattern, line):
                            report.issues.append(
                                AuditIssue(severity, msg, filename, i + 1)
                            )
            except Exception:
                pass  # Ignore read errors
