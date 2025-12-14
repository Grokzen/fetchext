import sys
import shutil
import subprocess
import logging
from pathlib import Path
from ..console import console
from ..config import load_config, get_config_value

logger = logging.getLogger(__name__)

DEFAULT_RULES_REPO = "https://github.com/Yara-Rules/rules.git"
DEFAULT_RULES_DIR = Path.home() / ".local" / "share" / "fetchext" / "rules"

def register(subparsers):
    rules_parser = subparsers.add_parser("rules", help="Manage analysis rules")
    rules_subparsers = rules_parser.add_subparsers(dest="rules_command", required=True, help="Rules action")

    # Sync subcommand
    sync_parser = rules_subparsers.add_parser("sync", help="Sync rules from a git repository")
    sync_parser.add_argument(
        "--repo",
        help=f"Git repository URL (default: {DEFAULT_RULES_REPO})"
    )
    sync_parser.add_argument(
        "--dir",
        type=Path,
        help=f"Directory to store rules (default: {DEFAULT_RULES_DIR})"
    )
    sync_parser.set_defaults(func=handle_sync)

    # List subcommand
    list_parser = rules_subparsers.add_parser("list", help="List installed rules")
    list_parser.add_argument(
        "--dir",
        type=Path,
        help=f"Directory to store rules (default: {DEFAULT_RULES_DIR})"
    )
    list_parser.set_defaults(func=handle_list)

def get_rules_config(args):
    config = load_config()
    
    repo = args.repo or get_config_value(config, "rules.repo") or DEFAULT_RULES_REPO
    
    rules_dir = args.dir
    if not rules_dir:
        config_dir = get_config_value(config, "rules.dir")
        if config_dir:
            rules_dir = Path(config_dir)
        else:
            rules_dir = DEFAULT_RULES_DIR
            
    return repo, rules_dir

def handle_sync(args, show_progress=True):
    if not shutil.which("git"):
        console.print("[red]Error: 'git' is not installed. Please install git to sync rules.[/red]")
        sys.exit(1)

    repo_url, rules_dir = get_rules_config(args)
    
    if not rules_dir.exists():
        console.print(f"[bold]Cloning rules from {repo_url} to {rules_dir}...[/bold]")
        try:
            rules_dir.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(
                ["git", "clone", repo_url, str(rules_dir)],
                check=True,
                stdout=subprocess.PIPE if not show_progress else None,
                stderr=subprocess.PIPE if not show_progress else None
            )
            console.print("[green]Rules cloned successfully.[/green]")
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Failed to clone rules: {e}[/red]")
            sys.exit(1)
    else:
        console.print(f"[bold]Updating rules in {rules_dir}...[/bold]")
        try:
            subprocess.run(
                ["git", "-C", str(rules_dir), "pull"],
                check=True,
                stdout=subprocess.PIPE if not show_progress else None,
                stderr=subprocess.PIPE if not show_progress else None
            )
            console.print("[green]Rules updated successfully.[/green]")
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Failed to update rules: {e}[/red]")
            sys.exit(1)

def handle_list(args, show_progress=True):
    _, rules_dir = get_rules_config(args)
    
    if not rules_dir.exists():
        console.print(f"[yellow]Rules directory {rules_dir} does not exist. Run 'fext rules sync' first.[/yellow]")
        return

    console.print(f"[bold]Rules in {rules_dir}:[/bold]")
    
    # Simple tree walk
    count = 0
    for path in rules_dir.rglob("*.yar*"):
        console.print(f"  - {path.relative_to(rules_dir)}")
        count += 1
        
    if count == 0:
        console.print("[yellow]No .yar or .yara files found.[/yellow]")
    else:
        console.print(f"\n[green]Found {count} rule files.[/green]")
