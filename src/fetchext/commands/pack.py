import logging
from pathlib import Path
from fetchext.packer import pack_extension
from fetchext.console import console

logger = logging.getLogger(__name__)


def register(subparsers):
    parser = subparsers.add_parser(
        "pack", help="Pack a directory into a signed CRX3 file"
    )
    add_arguments(parser)
    parser.set_defaults(func=lambda args, **kwargs: handle_pack(args))


def add_arguments(parser):
    parser.add_argument(
        "directory", help="Directory containing the extension source code"
    )
    parser.add_argument("-o", "--output", help="Output CRX file path")
    parser.add_argument(
        "-k",
        "--key",
        help="Private key file (PEM). If not provided, one will be generated.",
    )


def handle_pack(args):
    source_dir = Path(args.directory)
    if not source_dir.exists() or not source_dir.is_dir():
        console.print(f"[bold red]Error:[/bold red] Directory not found: {source_dir}")
        return 1

    try:
        output_path = pack_extension(source_dir, args.output, args.key)
        console.print(
            f"[bold green]Success![/bold green] Packed extension to {output_path}"
        )

        # If key was generated (or used default), mention it
        if not args.key:
            # Logic in packer is: if key_path is None, use output_path.with_suffix(".pem")
            # But we don't know for sure if it was generated or existed unless we check
            # However, packer returns output_path.
            # We can infer the key path.
            if args.output:
                key_path = Path(args.output).with_suffix(".pem")
            else:
                key_path = source_dir.with_suffix(".pem")

            if key_path.exists():
                console.print(f"[dim]Private key: {key_path}[/dim]")

    except Exception as e:
        console.print(f"[bold red]Pack failed:[/bold red] {e}")
        logger.exception("Pack failed")
        return 1

    return 0
