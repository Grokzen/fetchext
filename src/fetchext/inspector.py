import json
import logging
from rich.table import Table
from .console import console
from .utils import open_extension_archive

logger = logging.getLogger(__name__)

class ExtensionInspector:
    def get_manifest(self, file_path):
        try:
            with open_extension_archive(file_path) as zf:
                if "manifest.json" not in zf.namelist():
                    raise ValueError("manifest.json not found in archive")

                with zf.open("manifest.json") as f:
                    return json.load(f)

        except Exception as e:
            logger.error(f"Failed to inspect file: {e}")
            raise ValueError("Could not parse file as extension archive") from e

    def inspect(self, file_path):
        try:
            manifest = self.get_manifest(file_path)
            self._print_manifest_details(manifest)
        except Exception as e:
            logger.error(f"Inspection failed: {e}")

    def _print_manifest_details(self, manifest):
        table = Table(title="Extension Details", show_header=True, header_style="bold magenta")
        table.add_column("Field", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")

        table.add_row("Name", manifest.get('name', 'N/A'))
        table.add_row("Version", manifest.get('version', 'N/A'))
        table.add_row("Manifest Version", str(manifest.get('manifest_version', 'N/A')))
        table.add_row("Description", manifest.get('description', 'N/A'))

        permissions = manifest.get('permissions', [])
        if permissions:
            table.add_row("Permissions", "\n".join(f"- {p}" for p in permissions))
        else:
            table.add_row("Permissions", "None")

        host_permissions = manifest.get('host_permissions', [])
        if host_permissions:
            table.add_row("Host Permissions", "\n".join(f"- {p}" for p in host_permissions))
        
        console.print(table)
