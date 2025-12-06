import sys
import logging
import argparse
from pathlib import Path
from rich.logging import RichHandler
from .console import console
from .config import load_config
from . import core

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console, rich_tracebacks=True)]
)
logger = logging.getLogger("fetchext")

def get_parser():
    """
    Constructs and returns the argument parser.
    """
    # Load configuration
    config = load_config()
    general_config = config.get("general", {})
    batch_config = config.get("batch", {})

    default_output_dir = Path(general_config.get("download_dir", "."))
    default_workers = batch_config.get("workers", 4)
    default_save_metadata = general_config.get("save_metadata", False)
    default_extract = general_config.get("extract", False)

    parser = argparse.ArgumentParser(description="Download or search for browser extensions.")
    
    # Global logging flags
    logging_group = parser.add_mutually_exclusive_group()
    logging_group.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging (DEBUG level)"
    )
    logging_group.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Enable quiet mode (ERROR level only, no progress bars)"
    )

    subparsers = parser.add_subparsers(dest="command", required=True, help="Command to execute")

    # Download subcommand
    download_parser = subparsers.add_parser("download", aliases=["d"], help="Download an extension")
    download_parser.add_argument(
        "browser",
        choices=["chrome", "c", "edge", "e", "firefox", "f"],
        help="The browser type (chrome/c, edge/e, firefox/f)"
    )
    download_parser.add_argument("url", help="The URL of the extension in the Web Store")
    download_parser.add_argument(
        "-o", "--output-dir",
        type=Path,
        default=default_output_dir,
        help=f"Directory to save the downloaded extension (default: {default_output_dir})"
    )
    download_parser.add_argument(
        "-m", "--save-metadata",
        action="store_true",
        default=default_save_metadata,
        help="Save metadata to a JSON file alongside the extension"
    )
    download_parser.add_argument(
        "-x", "--extract",
        action="store_true",
        default=default_extract,
        help="Automatically extract the extension to a folder"
    )

    # Search subcommand
    search_parser = subparsers.add_parser("search", aliases=["s"], help="Search for an extension")
    search_parser.add_argument(
        "browser",
        choices=["firefox", "f"],
        help="The browser type (only firefox/f supported for search)"
    )
    search_parser.add_argument("query", help="The search query")
    search_group = search_parser.add_mutually_exclusive_group()
    search_group.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    search_group.add_argument(
        "--csv",
        action="store_true",
        help="Output results as CSV"
    )

    # Inspect subcommand
    inspect_parser = subparsers.add_parser("inspect", aliases=["i"], help="Inspect an extension file")
    inspect_parser.add_argument("file", help="Path to the .crx or .xpi file")
    inspect_parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    # Extract subcommand
    extract_parser = subparsers.add_parser("extract", aliases=["x"], help="Extract an extension file")
    extract_parser.add_argument("file", help="Path to the .crx or .xpi file")
    extract_parser.add_argument(
        "-o", "--output-dir",
        type=Path,
        help="Directory to extract to (default: <filename_stem> in current dir)"
    )

    # Check subcommand
    check_parser = subparsers.add_parser("check", aliases=["c"], help="Check for updates")
    check_parser.add_argument("file", help="Path to the .crx or .xpi file")
    check_parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    # Preview subcommand
    preview_parser = subparsers.add_parser("preview", aliases=["p"], help="Preview extension contents")
    preview_parser.add_argument("file", help="Path to the .crx or .xpi file")

    # Audit subcommand
    audit_parser = subparsers.add_parser("audit", aliases=["a"], help="Audit extension for MV3 compatibility")
    audit_parser.add_argument("file", help="Path to the .crx or .xpi file")
    audit_parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    # Diff subcommand
    diff_parser = subparsers.add_parser("diff", help="Compare two extension versions")
    diff_parser.add_argument("old_file", help="Path to the old .crx or .xpi file")
    diff_parser.add_argument("new_file", help="Path to the new .crx or .xpi file")
    diff_parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    # Risk subcommand
    risk_parser = subparsers.add_parser("risk", aliases=["r"], help="Analyze permission risk")
    risk_parser.add_argument("file", help="Path to the .crx or .xpi file")
    risk_parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    # Verify subcommand
    verify_parser = subparsers.add_parser("verify", help="Verify CRX signature")
    verify_parser.add_argument("file", help="Path to the .crx file")
    verify_parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    # Scan subcommand
    scan_parser = subparsers.add_parser("scan", help="Scan extension for vulnerable dependencies")
    scan_parser.add_argument("file", help="Path to the .crx or .xpi file")
    scan_group = scan_parser.add_mutually_exclusive_group()
    scan_group.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    scan_group.add_argument(
        "--csv",
        action="store_true",
        help="Output results as CSV"
    )

    # Report subcommand
    report_parser = subparsers.add_parser("report", help="Generate a Markdown report")
    report_parser.add_argument("file", help="Path to the .crx or .xpi file")
    report_parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output file path (default: <filename>_REPORT.md)"
    )

    # Update Manifest subcommand
    manifest_parser = subparsers.add_parser("update-manifest", aliases=["um"], help="Generate update manifest for local extensions")
    manifest_parser.add_argument("directory", type=Path, help="Directory containing extension files")
    manifest_parser.add_argument("--base-url", required=True, help="Base URL where extensions are hosted")
    manifest_parser.add_argument("--output", type=Path, help="Output file path (optional)")

    # Mirror subcommand
    mirror_parser = subparsers.add_parser("mirror", help="Sync local directory with extension list")
    mirror_parser.add_argument("list_file", type=Path, help="Path to the list file")
    mirror_parser.add_argument(
        "-o", "--output-dir",
        type=Path,
        default=default_output_dir,
        help=f"Target directory (default: {default_output_dir})"
    )
    mirror_parser.add_argument(
        "--prune",
        action="store_true",
        help="Remove files not in the list"
    )
    mirror_parser.add_argument(
        "-w", "--workers",
        type=int,
        default=default_workers,
        help=f"Number of parallel workers (default: {default_workers})"
    )

    # Batch subcommand
    batch_parser = subparsers.add_parser("batch", aliases=["b"], help="Download extensions from a batch file")
    batch_parser.add_argument("file", help="Path to the batch file containing URLs")
    batch_parser.add_argument(
        "-o", "--output-dir",
        type=Path,
        default=default_output_dir,
        help=f"Directory to save the downloaded extensions (default: {default_output_dir})"
    )
    batch_parser.add_argument(
        "-w", "--workers",
        type=int,
        default=default_workers,
        help=f"Number of parallel workers (default: {default_workers})"
    )

    # UI subcommand
    subparsers.add_parser("ui", help="Launch interactive TUI")

    # Setup subcommand
    subparsers.add_parser("setup", help="Run configuration wizard")

    # Convert subcommand
    convert_parser = subparsers.add_parser("convert", help="Convert extension format")
    convert_parser.add_argument("input", help="Input file or directory")
    convert_parser.add_argument(
        "--to",
        choices=["zip"],
        default="zip",
        help="Target format (default: zip)"
    )
    convert_parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output file path"
    )

    # Stats subcommand
    stats_parser = subparsers.add_parser("stats", help="Analyze repository statistics")
    stats_parser.add_argument(
        "directory",
        type=Path,
        nargs="?",
        default=Path("."),
        help="Directory to scan (default: current directory)"
    )
    stats_parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    # Analyze subcommand
    analyze_parser = subparsers.add_parser("analyze", help="Analyze extension code")
    analyze_parser.add_argument("file", help="Path to the .crx or .xpi file")
    analyze_parser.add_argument(
        "--complexity",
        action="store_true",
        help="Calculate cyclomatic complexity of JS files"
    )
    analyze_parser.add_argument(
        "--entropy",
        action="store_true",
        help="Calculate entropy of files to detect obfuscation/packing"
    )
    analyze_parser.add_argument(
        "--domains",
        action="store_true",
        help="Extract domains and URLs from source code"
    )
    analyze_parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    # Locales subcommand
    locales_parser = subparsers.add_parser("locales", help="Inspect extension locales")
    locales_parser.add_argument("file", help="Path to the .crx or .xpi file")
    locales_parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    # Explain subcommand
    explain_parser = subparsers.add_parser("explain", help="Explain a permission")
    explain_parser.add_argument("permission", help="The permission string to explain")
    explain_parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    
    return parser

def main():
    """
    Main entry point of the script.
    """
    parser = get_parser()
    args = parser.parse_args()

    # Configure logging based on flags
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.quiet:
        logger.setLevel(logging.ERROR)
        logging.getLogger().setLevel(logging.ERROR)
    
    # Determine if progress bars should be shown
    show_progress = not args.quiet

    if not args.quiet:
        logger.info("Starting fetchext...")

    try:
        if args.command in ["inspect", "i"]:
            core.inspect_extension(args.file, show_progress=show_progress, json_output=args.json)
            return

        if args.command in ["extract", "x"]:
            core.extract_extension(args.file, args.output_dir, show_progress=show_progress)
            return

        if args.command in ["check", "c"]:
            core.check_update(args.file, json_output=args.json)
            return

        if args.command in ["preview", "p"]:
            core.preview_extension(args.file)
            return

        if args.command in ["audit", "a"]:
            core.audit_extension(args.file, json_output=args.json)
            return

        if args.command == "diff":
            core.diff_extensions(args.old_file, args.new_file, json_output=args.json)
            return

        if args.command in ["risk", "r"]:
            core.analyze_risk(args.file, json_output=args.json)
            return

        if args.command == "verify":
            if core.verify_signature(args.file, json_output=args.json):
                sys.exit(0)
            else:
                sys.exit(1)

        if args.command == "scan":
            core.scan_extension(args.file, json_output=args.json, csv_output=args.csv)
            return

        if args.command == "report":
            core.generate_report(args.file, args.output)
            return

        if args.command in ["update-manifest", "um"]:
            from .server import generate_update_manifest
            generate_update_manifest(args.directory, args.base_url, args.output)
            return

        if args.command == "mirror":
            from .mirror import MirrorManager
            manager = MirrorManager()
            manager.sync(args.list_file, args.output_dir, prune=args.prune, workers=args.workers, show_progress=show_progress)
            return

        if args.command in ["batch", "b"]:
            core.batch_download(args.file, args.output_dir, workers=args.workers, show_progress=show_progress)
            return

        if args.command == "ui":
            from .tui import run_tui
            run_tui()
            return

        if args.command == "setup":
            from .setup import run_setup
            run_setup()
            return

        if args.command == "convert":
            core.convert_extension(args.input, args.output, to_format=args.to)
            return

        if args.command == "stats":
            core.get_repo_stats(args.directory, json_output=args.json)
            return

        if args.command == "analyze":
            if args.complexity:
                from .analysis.complexity import analyze_complexity
                import json
                from rich.table import Table
                
                results = analyze_complexity(Path(args.file))
                
                if args.json:
                    print(json.dumps(results, indent=2))
                else:
                    console.print(f"[bold]Complexity Analysis for {args.file}[/bold]")
                    console.print(f"Average Complexity: {results['average_complexity']:.2f}")
                    console.print(f"Max Complexity: {results['max_complexity']}")
                    console.print(f"Total Functions: {results['total_functions']}")
                    
                    if results["high_complexity_functions"]:
                        console.print("\n[bold red]High Complexity Functions (>15):[/bold red]")
                        table = Table(show_header=True, header_style="bold magenta")
                        table.add_column("File")
                        table.add_column("Function")
                        table.add_column("Complexity")
                        table.add_column("Length")
                        
                        for func in results["high_complexity_functions"]:
                            table.add_row(
                                func["file"],
                                func["function"],
                                str(func["complexity"]),
                                str(func["length"])
                            )
                        console.print(table)
                    else:
                        console.print("\n[green]No high complexity functions found.[/green]")
            
            elif args.entropy:
                from .analysis.entropy import analyze_entropy
                import json
                from rich.table import Table
                
                results = analyze_entropy(Path(args.file))
                
                if args.json:
                    print(json.dumps(results, indent=2))
                else:
                    console.print(f"[bold]Entropy Analysis for {args.file}[/bold]")
                    console.print(f"Average Entropy: {results['average_entropy']:.2f}")
                    
                    # Sort by entropy descending
                    sorted_files = sorted(results["files"], key=lambda x: x["entropy"], reverse=True)
                    
                    table = Table(show_header=True, header_style="bold magenta")
                    table.add_column("File")
                    table.add_column("Entropy")
                    table.add_column("Size")
                    table.add_column("Verdict")
                    
                    for file_info in sorted_files[:20]:  # Show top 20
                        entropy = file_info["entropy"]
                        verdict = "[green]Normal[/green]"
                        if entropy > 7.5:
                            verdict = "[red]Packed/Encrypted[/red]"
                        elif entropy > 6.0:
                            verdict = "[yellow]High[/yellow]"
                            
                        table.add_row(
                            file_info["filename"],
                            f"{entropy:.2f}",
                            str(file_info["size"]),
                            verdict
                        )
                    console.print(table)
                    if len(sorted_files) > 20:
                        console.print(f"\n... and {len(sorted_files) - 20} more files.")
            
            elif args.domains:
                from .analysis.domains import analyze_domains
                import json
                from rich.table import Table
                
                results = analyze_domains(Path(args.file))
                
                if args.json:
                    print(json.dumps(results, indent=2))
                else:
                    console.print(f"[bold]Domain Analysis for {args.file}[/bold]")
                    
                    console.print(f"\n[bold cyan]Unique Domains ({len(results['domains'])}):[/bold cyan]")
                    if results["domains"]:
                        for domain in results["domains"]:
                            console.print(f"  - {domain}")
                    else:
                        console.print("  [yellow]No domains found.[/yellow]")
                        
                    console.print(f"\n[bold cyan]URLs ({len(results['urls'])}):[/bold cyan]")
                    if results["urls"]:
                        # Show top 50 URLs to avoid spamming
                        for url in results["urls"][:50]:
                            console.print(f"  - {url}")
                        if len(results["urls"]) > 50:
                            console.print(f"  ... and {len(results['urls']) - 50} more.")
                    else:
                        console.print("  [yellow]No URLs found.[/yellow]")
            return

        if args.command == "locales":
            from .analysis.locales import inspect_locales
            import json
            from rich.table import Table
            
            results = inspect_locales(Path(args.file))
            
            if args.json:
                print(json.dumps(results, indent=2))
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
            return

        if args.command == "explain":
            from .analysis.explainer import explain_permission
            import json
            from rich.panel import Panel
            
            result = explain_permission(args.permission)
            
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                if result:
                    risk_color = {
                        "Low": "green",
                        "Medium": "yellow",
                        "High": "red",
                        "Critical": "bold red"
                    }.get(result["risk"], "white")
                    
                    console.print(Panel(
                        f"[bold]Description:[/bold] {result['description']}\n\n"
                        f"[bold]Risk Level:[/bold] [{risk_color}]{result['risk']}[/{risk_color}]",
                        title=f"[bold cyan]{args.permission}[/bold cyan]",
                        expand=False
                    ))
                else:
                    console.print(f"[red]Permission '{args.permission}' not found in database.[/red]")
            return

        if args.command in ["download", "d"]:
            core.download_extension(
                args.browser,
                args.url,
                args.output_dir,
                save_metadata=args.save_metadata,
                extract=args.extract,
                show_progress=show_progress
            )

        elif args.command in ["search", "s"]:
            core.search_extension(args.browser, args.query, json_output=args.json, csv_output=args.csv)

        if not args.quiet:
            logger.info("Script finished successfully.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
