import sys
from pathlib import Path
from .. import core
from ..console import console

def register(subparsers):
    # Inspect subcommand
    inspect_parser = subparsers.add_parser("inspect", aliases=["i"], help="Inspect an extension file")
    inspect_parser.add_argument("file", help="Path to the .crx or .xpi file")
    inspect_parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    inspect_parser.set_defaults(func=handle_inspect)

    # Preview subcommand
    preview_parser = subparsers.add_parser("preview", aliases=["p"], help="Preview extension contents")
    preview_parser.add_argument("file", help="Path to the .crx or .xpi file")
    preview_parser.set_defaults(func=handle_preview)

    # Diff subcommand
    diff_parser = subparsers.add_parser("diff", help="Compare two extension versions")
    diff_parser.add_argument("old_file", help="Path to the old .crx or .xpi file")
    diff_parser.add_argument("new_file", help="Path to the new .crx or .xpi file")
    diff_parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    diff_parser.add_argument(
        "-w", "--ignore-whitespace",
        action="store_true",
        help="Ignore whitespace changes in text files"
    )
    diff_parser.add_argument(
        "--visual",
        action="store_true",
        help="Generate a visual HTML diff report"
    )
    diff_parser.add_argument(
        "--output",
        type=Path,
        help="Output path for the visual report (default: diff_report.html)"
    )
    diff_parser.set_defaults(func=handle_diff)

    # Verify subcommand
    verify_parser = subparsers.add_parser("verify", help="Verify CRX signature")
    verify_parser.add_argument("file", help="Path to the .crx file")
    verify_parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    verify_parser.set_defaults(func=handle_verify)

    # Locales subcommand
    locales_parser = subparsers.add_parser("locales", help="Inspect extension locales")
    locales_parser.add_argument("file", help="Path to the .crx or .xpi file")
    locales_parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    locales_parser.set_defaults(func=handle_locales)

def handle_inspect(args, show_progress=True):
    core.inspect_extension(args.file, show_progress=show_progress, json_output=args.json)

def handle_preview(args, show_progress=True):
    core.preview_extension(args.file)

def handle_diff(args, show_progress=True):
    core.diff_extensions(
        args.old_file, 
        args.new_file, 
        json_output=args.json,
        ignore_whitespace=args.ignore_whitespace,
        visual=args.visual,
        output_path=args.output
    )

def handle_verify(args, show_progress=True):
    if core.verify_signature(args.file, json_output=args.json):
        sys.exit(0)
    else:
        sys.exit(1)

def handle_locales(args, show_progress=True):
    from ..analysis.locales import inspect_locales
    from rich.table import Table
    
    results = inspect_locales(Path(args.file))
    
    if args.json:
        console.print_json(data=results)
    else:
        console.print(f"[bold]Locales for {args.file}[/bold]")
        if results["default_locale"]:
            console.print(f"Default Locale: [cyan]{results['default_locale']}[/cyan]")
        else:
            console.print("Default Locale: [yellow]Not specified[/yellow]")
        
        console.print(f"Supported Locales: {len(results['supported_locales'])}")
        
        if results["supported_locales"]:
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Locale")
            table.add_column("Messages")
            table.add_column("Status")
            
            for locale in sorted(results["supported_locales"]):
                details = results["details"][locale]
                status = "[red]Error[/red]" if "error" in details else "[green]OK[/green]"
                count = str(details.get("message_count", 0))
                table.add_row(locale, count, status)
            console.print(table)
        else:
            console.print("[yellow]No locales found in _locales directory.[/yellow]")
