import subprocess
import shutil
from pathlib import Path
from fetchext.interface.console  import console
from fetchext.core.constants  import ExitCode


def register(subparsers):
    parser = subparsers.add_parser("git", help="Git integration tools")
    git_subparsers = parser.add_subparsers(dest="git_command", required=True)

    # Init command
    init_parser = git_subparsers.add_parser(
        "init", help="Initialize a git repository for an extension"
    )
    init_parser.add_argument("directory", type=Path, help="Directory to initialize")
    init_parser.add_argument(
        "--no-commit", action="store_true", help="Do not make an initial commit"
    )

    parser.set_defaults(func=handle_git)


def handle_git(args, show_progress=True):
    if args.git_command == "init":
        handle_init(args)


def handle_init(args):
    target_dir = args.directory.resolve()

    if not target_dir.exists():
        console.print(f"[red]Directory not found: {target_dir}[/red]")
        raise SystemExit(ExitCode.IO)

    if not shutil.which("git"):
        console.print("[red]Git is not installed or not in PATH.[/red]")
        raise SystemExit(ExitCode.DEPENDENCY)

    # Check if already a git repo
    if (target_dir / ".git").exists():
        console.print(
            f"[yellow]Directory is already a git repository: {target_dir}[/yellow]"
        )
        return

    try:
        # git init
        subprocess.run(["git", "init"], cwd=target_dir, check=True, capture_output=True)
        console.print(
            f"[green]Initialized empty Git repository in {target_dir}[/green]"
        )

        # Create .gitignore
        gitignore_path = target_dir / ".gitignore"
        if not gitignore_path.exists():
            gitignore_content = """
# Fetchext / Browser Extension
*.crx
*.xpi
*.pem
*.zip
node_modules/
__pycache__/
.DS_Store
Thumbs.db
.env
dist/
build/
coverage/
"""
            gitignore_path.write_text(gitignore_content.strip())
            console.print("[green]Created .gitignore[/green]")

        if not args.no_commit:
            # git add .
            subprocess.run(
                ["git", "add", "."], cwd=target_dir, check=True, capture_output=True
            )

            # git commit
            subprocess.run(
                ["git", "commit", "-m", "Initial commit (fext)"],
                cwd=target_dir,
                check=True,
                capture_output=True,
            )
            console.print("[green]Created initial commit[/green]")

    except subprocess.CalledProcessError as e:
        console.print(f"[red]Git command failed: {e}[/red]")
        if e.stderr:
            console.print(f"[red]{e.stderr.decode()}[/red]")
        raise SystemExit(ExitCode.ERROR)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise SystemExit(ExitCode.ERROR)
