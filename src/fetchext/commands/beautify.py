from pathlib import Path
from fetchext.workflow.beautify  import CodeBeautifier
from fetchext.interface.console  import console


def register(subparsers):
    parser = subparsers.add_parser(
        "beautify", aliases=["fmt"], help="Beautify JavaScript and JSON files"
    )
    parser.add_argument("path", help="File or directory to beautify")
    parser.add_argument(
        "-i", "--in-place", action="store_true", help="Modify file(s) in place"
    )
    parser.add_argument(
        "-o", "--output", type=Path, help="Output file path (only for single file)"
    )
    parser.set_defaults(func=handle_beautify)


def handle_beautify(args, show_progress=True):
    beautifier = CodeBeautifier()
    path = Path(args.path)

    if path.is_dir():
        if args.output:
            console.print("[red]Error: --output cannot be used with a directory.[/red]")
            return

        if not args.in_place:
            console.print(
                "[yellow]Warning: Beautifying a directory requires --in-place. Assuming --in-place.[/yellow]"
            )

        console.print(f"Beautifying directory: {path}")
        beautifier.beautify_directory(path, in_place=True)
        console.print("[green]Directory beautified successfully.[/green]")

    elif path.is_file():
        result = beautifier.beautify_file(
            path, in_place=args.in_place, output_path=args.output
        )

        if not args.in_place and not args.output:
            print(result)
        else:
            console.print(f"[green]File beautified successfully: {path}[/green]")
    else:
        console.print(f"[red]Path not found: {path}[/red]")
