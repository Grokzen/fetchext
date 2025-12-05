import json
from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple
from pathlib import Path
from .utils import open_extension_archive

@dataclass
class DiffReport:
    old_version: str
    new_version: str
    manifest_changes: Dict[str, Tuple[Any, Any]] = field(default_factory=dict)
    added_files: List[str] = field(default_factory=list)
    removed_files: List[str] = field(default_factory=list)
    modified_files: List[str] = field(default_factory=list)

class ExtensionDiffer:
    def diff(self, old_path: Path, new_path: Path) -> DiffReport:
        with open_extension_archive(old_path) as old_zf, \
             open_extension_archive(new_path) as new_zf:
            
            # Manifest Diff
            old_manifest = self._read_manifest(old_zf)
            new_manifest = self._read_manifest(new_zf)
            
            manifest_changes = self._diff_manifests(old_manifest, new_manifest)
            
            # File Diff
            old_files = {info.filename: info for info in old_zf.infolist()}
            new_files = {info.filename: info for info in new_zf.infolist()}
            
            added = []
            removed = []
            modified = []
            
            all_files = set(old_files.keys()) | set(new_files.keys())
            
            for filename in sorted(all_files):
                if filename not in old_files:
                    added.append(filename)
                elif filename not in new_files:
                    removed.append(filename)
                else:
                    # Check modification
                    old_info = old_files[filename]
                    new_info = new_files[filename]
                    
                    # Compare CRC32
                    if old_info.CRC != new_info.CRC:
                        modified.append(filename)
                    elif old_info.file_size != new_info.file_size:
                        modified.append(filename)
                        
            return DiffReport(
                old_version=old_manifest.get("version", "unknown"),
                new_version=new_manifest.get("version", "unknown"),
                manifest_changes=manifest_changes,
                added_files=added,
                removed_files=removed,
                modified_files=modified
            )

    def _read_manifest(self, zf) -> Dict:
        try:
            return json.loads(zf.read("manifest.json"))
        except Exception:
            return {}

    def _diff_manifests(self, old: Dict, new: Dict) -> Dict[str, Tuple[Any, Any]]:
        changes = {}
        # Check keys in both or either
        all_keys = set(old.keys()) | set(new.keys())
        
        for key in all_keys:
            old_val = old.get(key)
            new_val = new.get(key)
            
            if old_val != new_val:
                changes[key] = (old_val, new_val)
                
        return changes
