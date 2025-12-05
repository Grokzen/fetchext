import json
import zipfile
import logging
from io import BytesIO
from pathlib import Path
from rich.table import Table
from .console import console

logger = logging.getLogger(__name__)

class ExtensionInspector:
    def get_manifest(self, file_path):
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        try:
            with zipfile.ZipFile(path, 'r') as zf:
                if "manifest.json" not in zf.namelist():
                    raise ValueError("manifest.json not found in archive")

                with zf.open("manifest.json") as f:
                    return json.load(f)

        except zipfile.BadZipFile:
            # CRX files might have a header before the ZIP content
            # This is a simple fallback to try and find the start of the ZIP
            try:
                with open(path, 'rb') as f:
                    content = f.read()
                    # ZIP local file header signature is 0x04034b50
                    zip_start = content.find(b'PK\x03\x04')
                    if zip_start == -1:
                        raise ValueError("Not a valid ZIP or CRX file")
                    
                    # Read into BytesIO from offset
                    f.seek(zip_start)
                    with zipfile.ZipFile(BytesIO(f.read()), 'r') as zf:
                         if "manifest.json" not in zf.namelist():
                            raise ValueError("manifest.json not found in archive")
                         with zf.open("manifest.json") as f_manifest:
                            return json.load(f_manifest)

            except Exception as e:
                logger.error(f"Failed to inspect file: {e}")
                raise ValueError("Could not parse file as extension archive")

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
