import json
import zipfile
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ExtensionInspector:
    def inspect(self, file_path):
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        try:
            with zipfile.ZipFile(path, 'r') as zf:
                if "manifest.json" not in zf.namelist():
                    raise ValueError("manifest.json not found in archive")

                with zf.open("manifest.json") as f:
                    manifest = json.load(f)
                    self._print_manifest_details(manifest)

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
                    
                    # We can't easily use zipfile on a memory buffer with an offset without BytesIO
                    # But for CRX3, the header is complex. 
                    # Let's try a simpler approach: many CRX files are just ZIPs or have a small header.
                    # If standard ZipFile failed, it might be a CRX with a header.
                    # Python's zipfile module is strict.
                    
                    # Alternative: Read into BytesIO from offset
                    from io import BytesIO
                    f.seek(zip_start)
                    with zipfile.ZipFile(BytesIO(f.read()), 'r') as zf:
                         if "manifest.json" not in zf.namelist():
                            raise ValueError("manifest.json not found in archive")
                         with zf.open("manifest.json") as f_manifest:
                            manifest = json.load(f_manifest)
                            self._print_manifest_details(manifest)
                            return

            except Exception as e:
                logger.error(f"Failed to inspect file: {e}")
                raise ValueError("Could not parse file as extension archive")

    def _print_manifest_details(self, manifest):
        print("Extension Details:")
        print(f"  Name: {manifest.get('name', 'N/A')}")
        print(f"  Version: {manifest.get('version', 'N/A')}")
        print(f"  Manifest Version: {manifest.get('manifest_version', 'N/A')}")
        print(f"  Description: {manifest.get('description', 'N/A')}")
        
        permissions = manifest.get('permissions', [])
        if permissions:
            print("  Permissions:")
            for p in permissions:
                print(f"    - {p}")
        else:
            print("  Permissions: None")
        
        host_permissions = manifest.get('host_permissions', [])
        if host_permissions:
            print("  Host Permissions:")
            for p in host_permissions:
                print(f"    - {p}")
