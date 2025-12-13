from pathlib import Path
from typing import Dict, Set, Any
from ..inspector import ExtensionInspector

class PermissionMatrixGenerator:
    def generate(self, directory: Path) -> Dict[str, Any]:
        inspector = ExtensionInspector()
        extensions_data = []
        all_permissions: Set[str] = set()

        # Find all extension files
        files = []
        if directory.is_file():
             files = [directory]
        elif directory.exists():
             files = list(directory.glob("*.crx")) + \
                     list(directory.glob("*.xpi")) + \
                     list(directory.glob("*.zip"))

        for file_path in files:
            try:
                manifest = inspector.get_manifest(file_path)
                perms = set(manifest.get("permissions", []))
                
                # Add host permissions if present (MV3)
                if "host_permissions" in manifest:
                    perms.update(manifest["host_permissions"])
                
                # Add optional permissions
                if "optional_permissions" in manifest:
                    perms.update(manifest["optional_permissions"])

                # Normalize permissions (remove duplicates, sort)
                perms_list = sorted(list(perms))
                all_permissions.update(perms_list)

                extensions_data.append({
                    "filename": file_path.name,
                    "permissions": perms_list
                })
            except Exception:
                # Skip invalid files or log error
                continue

        sorted_permissions = sorted(list(all_permissions))
        
        # Build matrix
        matrix = {}
        for ext in extensions_data:
            row = {}
            ext_perms = set(ext["permissions"])
            for p in sorted_permissions:
                row[p] = p in ext_perms
            matrix[ext["filename"]] = row

        return {
            "permissions": sorted_permissions,
            "extensions": extensions_data,
            "matrix": matrix
        }
