import shutil
from pathlib import Path
from rich.console import Console
from rich.prompt import Confirm

console = Console()

def get_size(path: Path) -> int:
    """Calculate the size of a file or directory."""
    total = 0
    if path.is_file():
        return path.stat().st_size
    if path.is_dir():
        for p in path.rglob('*'):
            if p.is_file():
                total += p.stat().st_size
    return total

def format_size(size: int) -> str:
    """Format size in bytes to human readable string."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"

def clean_artifacts(
    base_dir: Path,
    clean_cache: bool = True,
    clean_downloads: bool = False,
    download_dir: Path = None,
    dry_run: bool = False,
    force: bool = False
) -> None:
    """
    Clean up artifacts and caches.
    """
    targets = []
    
    if clean_cache:
        # Standard Python/Build artifacts
        targets.extend([
            base_dir / "build",
            base_dir / "dist",
            base_dir / ".pytest_cache",
            base_dir / ".mypy_cache",
            base_dir / ".ruff_cache",
            base_dir / ".tox",
            base_dir / ".venv",
            base_dir / "venv",
        ])
        
        # Egg info
        targets.extend(base_dir.rglob("*.egg-info"))
        
        # Pycache
        targets.extend(base_dir.rglob("__pycache__"))

    if clean_downloads and download_dir:
        targets.append(download_dir)

    # Filter existing targets
    existing_targets = [t for t in targets if t.exists()]
    
    if not existing_targets:
        console.print("[yellow]Nothing to clean.[/yellow]")
        return

    total_size = sum(get_size(t) for t in existing_targets)
    
    console.print(f"[bold]Found {len(existing_targets)} items to clean ({format_size(total_size)}):[/bold]")
    for target in existing_targets:
        console.print(f"  - {target} ({format_size(get_size(target))})")

    if dry_run:
        console.print("[cyan]Dry run: No changes made.[/cyan]")
        return

    if not force:
        if not Confirm.ask("Are you sure you want to delete these items?"):
            console.print("[yellow]Aborted.[/yellow]")
            return

    reclaimed = 0
    for target in existing_targets:
        try:
            size = get_size(target)
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
            reclaimed += size
            console.print(f"[green]Deleted:[/green] {target}")
        except Exception as e:
            console.print(f"[red]Failed to delete {target}: {e}[/red]")

    console.print(f"[bold green]Clean complete. Reclaimed {format_size(reclaimed)}.[/bold green]")
