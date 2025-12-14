import subprocess
import shutil
from pathlib import Path
from ..console import console
from ..config import load_config, get_config_value
from ..constants import ExitCode

def register(subparsers):
    parser = subparsers.add_parser("rules", help="Manage analysis rules")
    rules_subparsers = parser.add_subparsers(dest="rules_command", required=True)

    # Sync command
    sync_parser = rules_subparsers.add_parser("sync", help="Sync community rules")
    sync_parser.add_argument(
        "--url",
        help="Git repository URL (overrides config)"
    )
    sync_parser.add_argument(
        "--dir",
        type=Path,
        help="Local directory to sync to (overrides config)"
    )
    
    parser.set_defaults(func=handle_rules)

def handle_rules(args, show_progress=True):
    if args.rules_command == "sync":
        handle_sync(args)

def handle_sync(args):
    config = load_config()
    
    # Determine URL
    repo_url = args.url or get_config_value(config, "rules.repo_url") or "https://github.com/fetchext/community-rules.git"
    
    # Determine Directory
    repo_dir_str = args.dir or get_config_value(config, "rules.repo_dir")
    if repo_dir_str:
        repo_dir = Path(repo_dir_str).expanduser().resolve()
    else:
        # Default to XDG_DATA_HOME or ~/.local/share
        import os
        xdg_data_home = os.environ.get("XDG_DATA_HOME")
        if xdg_data_home:
            base_dir = Path(xdg_data_home)
        else:
            base_dir = Path.home() / ".local" / "share"
        
        repo_dir = base_dir / "fext" / "rules"

    if not shutil.which("git"):
        console.print("[red]Git is not installed or not in PATH.[/red]")
        raise SystemExit(ExitCode.DEPENDENCY)

    console.print(f"Syncing rules from [cyan]{repo_url}[/cyan] to [cyan]{repo_dir}[/cyan]...")

    try:
        if repo_dir.exists():
            if (repo_dir / ".git").exists():
                # git pull
                console.print("Updating existing repository...")
                subprocess.run(["git", "pull"], cwd=repo_dir, check=True, capture_output=True)
                console.print("[green]Rules updated successfully.[/green]")
            else:
                console.print(f"[red]Directory {repo_dir} exists but is not a git repository.[/red]")
                console.print("Please remove it or specify a different directory.")
                raise SystemExit(ExitCode.IO)
        else:
            # git clone
            console.print("Cloning new repository...")
            repo_dir.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(["git", "clone", repo_url, str(repo_dir)], check=True, capture_output=True)
            console.print("[green]Rules cloned successfully.[/green]")

    except subprocess.CalledProcessError as e:
        console.print(f"[red]Git command failed: {e}[/red]")
        if e.stderr:
            console.print(f"[red]{e.stderr.decode()}[/red]")
        raise SystemExit(ExitCode.ERROR)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise SystemExit(ExitCode.ERROR)
