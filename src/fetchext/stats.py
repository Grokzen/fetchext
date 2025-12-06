from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Counter
import json
from rich.console import Console
from rich.table import Table
from rich.progress import track
from .utils import open_extension_archive

@dataclass
class RepoStats:
    total_files: int = 0
    total_size_bytes: int = 0
    mv2_count: int = 0
    mv3_count: int = 0
    permissions: Counter = field(default_factory=Counter)
    host_permissions: Counter = field(default_factory=Counter)
    errors: List[str] = field(default_factory=list)

class RepoAnalyzer:
    def scan(self, directory: Path) -> RepoStats:
        stats = RepoStats()
        # Find all CRX and ZIP files
        files = list(directory.glob("*.crx")) + list(directory.glob("*.zip"))
        
        # Use track for progress bar
        for file_path in track(files, description="Scanning repository..."):
            stats.total_files += 1
            stats.total_size_bytes += file_path.stat().st_size
            
            try:
                with open_extension_archive(file_path) as zf:
                    try:
                        manifest_data = zf.read("manifest.json")
                        manifest = json.loads(manifest_data)
                        
                        mv = manifest.get("manifest_version", 0)
                        if mv == 2:
                            stats.mv2_count += 1
                        elif mv == 3:
                            stats.mv3_count += 1
                            
                        # Parse permissions
                        for perm in manifest.get("permissions", []):
                            # Heuristic: if it looks like a URL pattern, treat as host permission
                            if "://" in perm or perm == "<all_urls>":
                                stats.host_permissions[perm] += 1
                            else:
                                stats.permissions[perm] += 1
                        
                        # Parse host_permissions (MV3 specific)
                        if "host_permissions" in manifest:
                             for perm in manifest["host_permissions"]:
                                 stats.host_permissions[perm] += 1
                                 
                    except (KeyError, json.JSONDecodeError):
                        stats.errors.append(f"{file_path.name}: Invalid/Missing manifest")
            except Exception as e:
                stats.errors.append(f"{file_path.name}: {str(e)}")
                
        return stats

def print_stats(stats: RepoStats):
    console = Console()
    
    # General Table
    table = Table(title="Repository Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")
    
    table.add_row("Total Extensions", str(stats.total_files))
    table.add_row("Total Size", f"{stats.total_size_bytes / 1024 / 1024:.2f} MB")
    table.add_row("Manifest V2", str(stats.mv2_count))
    table.add_row("Manifest V3", str(stats.mv3_count))
    table.add_row("Errors", str(len(stats.errors)))
    
    console.print(table)
    console.print()
    
    # Permissions Table
    perm_table = Table(title="Top 10 Permissions")
    perm_table.add_column("Permission", style="green")
    perm_table.add_column("Count", style="yellow")
    
    for perm, count in stats.permissions.most_common(10):
        perm_table.add_row(perm, str(count))
        
    console.print(perm_table)
    console.print()

    # Host Permissions Table
    host_table = Table(title="Top 10 Host Permissions")
    host_table.add_column("Host Pattern", style="blue")
    host_table.add_column("Count", style="yellow")
    
    for perm, count in stats.host_permissions.most_common(10):
        host_table.add_row(perm, str(count))
        
    console.print(host_table)
