import shutil
import subprocess
import sys
import logging
from pathlib import Path
from typing import List, Optional

from rich.console import Console

logger = logging.getLogger(__name__)
console = Console()


class DenoSandbox:
    def __init__(self):
        self.executable = shutil.which("deno")

    @property
    def is_available(self) -> bool:
        return self.executable is not None

    def run(
        self,
        file_path: Path,
        allow_net: bool = False,
        allow_read: bool = False,
        timeout: int = 5,
        args: Optional[List[str]] = None,
    ) -> subprocess.CompletedProcess:
        if not self.is_available:
            raise RuntimeError(
                "Deno is not installed. Please install Deno to use the sandbox feature: https://deno.land/"
            )

        cmd = [
            self.executable,
            "run",
            "--no-prompt",  # Non-interactive
        ]

        # Permissions
        if allow_net:
            cmd.append("--allow-net")
        if allow_read:
            cmd.append("--allow-read")

        # If no permissions are granted, Deno defaults to secure (no access)

        cmd.append(str(file_path))

        if args:
            cmd.extend(args)

        logger.debug(f"Running sandbox command: {' '.join(cmd)}")

        try:
            return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired as e:
            # Create a completed process object for the timeout case
            return subprocess.CompletedProcess(
                args=cmd,
                returncode=124,  # Standard timeout exit code
                stdout=e.stdout or "",
                stderr=e.stderr or f"Execution timed out after {timeout} seconds.",
            )


def register(subparsers):
    parser = subparsers.add_parser(
        "sandbox", help="Execute JS in a secure sandbox (requires Deno)"
    )
    parser.add_argument("file", type=Path, help="JavaScript file to execute")
    parser.add_argument("--allow-net", action="store_true", help="Allow network access")
    parser.add_argument(
        "--allow-read", action="store_true", help="Allow file system read access"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=5,
        help="Execution timeout in seconds (default: 5)",
    )
    parser.add_argument("args", nargs="*", help="Arguments to pass to the script")
    parser.set_defaults(func=handle_sandbox)


def handle_sandbox(args, show_progress=True):
    sandbox = DenoSandbox()

    if not sandbox.is_available:
        console.print("[red]Error: Deno is not installed.[/red]")
        console.print(
            "The sandbox feature requires Deno to provide a secure execution environment."
        )
        console.print(
            "Please install it from [link=https://deno.land/]https://deno.land/[/link]"
        )
        sys.exit(1)

    console.print(f"[bold blue]Sandboxing {args.file}...[/bold blue]")

    try:
        result = sandbox.run(
            args.file,
            allow_net=args.allow_net,
            allow_read=args.allow_read,
            timeout=args.timeout,
            args=args.args,
        )

        if result.stdout:
            console.print("[bold green]Output:[/bold green]")
            console.print(result.stdout)

        if result.stderr:
            console.print("[bold red]Errors:[/bold red]")
            console.print(result.stderr)

        if result.returncode != 0:
            sys.exit(result.returncode)

    except Exception as e:
        console.print(f"[bold red]Execution failed: {e}[/bold red]")
        sys.exit(1)
