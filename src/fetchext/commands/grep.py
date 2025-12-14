from pathlib import Path
from ..console import console
from ..analysis.grep import search_directory
from ..config import load_config


def register(subparsers):
    grep_parser = subparsers.add_parser(
        "grep", help="Search for pattern in all extensions"
    )
    grep_parser.add_argument("pattern", help="Regex pattern to search for")
    grep_parser.add_argument(
        "-d",
        "--directory",
        type=Path,
        help="Directory to search (default: configured download dir)",
    )
    grep_parser.add_argument(
        "-i", "--ignore-case", action="store_true", help="Ignore case"
    )
    grep_parser.add_argument(
        "--json", action="store_true", help="Output results as JSON"
    )
    grep_parser.set_defaults(func=handle_grep)


def handle_grep(args, show_progress=True):
    directory = args.directory
    if not directory:
        config = load_config()
        directory = Path(config.get("download_dir", "downloads"))

    if not directory.exists():
        console.print(f"[red]Directory not found: {directory}[/red]")
        return

    if show_progress:
        console.print(f"Searching for '{args.pattern}' in {directory}...")

    results = search_directory(directory, args.pattern, args.ignore_case)

    if args.json:
        console.print_json(data=results)
    else:
        if not results:
            console.print("[yellow]No matches found.[/yellow]")
            return

        from rich.table import Table

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("File")
        table.add_column("Line", justify="right")
        table.add_column("Content")

        # Group by file for cleaner output? Or just list?
        # Let's list for now, maybe limit output

        for match in results[:100]:  # Limit to 100 matches to avoid spam
            table.add_row(match["file"], str(match["line"]), match["content"])

        console.print(table)

        if len(results) > 100:
            console.print(
                f"\n[yellow]... and {len(results) - 100} more matches.[/yellow]"
            )
