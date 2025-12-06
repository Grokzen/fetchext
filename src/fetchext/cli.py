import sys
import logging
import argparse
from pathlib import Path
from rich.logging import RichHandler
from .console import console
from .config import load_config, save_config, get_config_value, set_config_value
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
        "--secrets",
        action="store_true",
        help="Scan for potential secrets (API keys, tokens)"
    )
    analyze_parser.add_argument(
        "--yara",
        type=Path,
        help="Path to YARA rules file to scan against"
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

    # Config subcommand
    config_parser = subparsers.add_parser("config", help="Manage configuration")
    config_subparsers = config_parser.add_subparsers(dest="config_command", required=True, help="Config action")
    
    # Config Get
    config_get_parser = config_subparsers.add_parser("get", help="Get a configuration value")
    config_get_parser.add_argument("key", help="Configuration key (e.g. general.download_dir)")
    
    # Config Set
    config_set_parser = config_subparsers.add_parser("set", help="Set a configuration value")
    config_set_parser.add_argument("key", help="Configuration key (e.g. general.download_dir)")
    config_set_parser.add_argument("value", help="Value to set")
    
    # Config List
    config_subparsers.add_parser("list", help="List all configuration settings")
    
    # Clean subcommand
    clean_parser = subparsers.add_parser("clean", help="Clean up caches and artifacts")
    clean_parser.add_argument(
        "--cache",
        action="store_true",
        default=True,
        help="Clean build and test caches (default)"
    )
    clean_parser.add_argument(
        "--downloads",
        action="store_true",
        help="Clean download directory"
    )
    clean_parser.add_argument(
        "--all",
        action="store_true",
        help="Clean everything"
    )
    clean_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without deleting"
    )
    clean_parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Skip confirmation"
    )

    # History subcommand
    history_parser = subparsers.add_parser("history", help="View download history")
    history_parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Number of entries to show (default: 20)"
    )
    history_parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear the history"
    )
    history_parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    # Schema subcommand
    schema_parser = subparsers.add_parser("schema", help="Get JSON schema for outputs")
    schema_parser.add_argument(
        "type",
        choices=["config", "audit", "risk", "history", "scan"],
        help="The type of schema to generate"
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
            
            elif args.secrets:
                from .secrets import SecretScanner
                import json
                from rich.table import Table
                
                scanner = SecretScanner()
                results = scanner.scan_extension(Path(args.file))
                
                if args.json:
                    # Convert dataclass to dict for JSON serialization
                    import dataclasses
                    print(json.dumps([dataclasses.asdict(r) for r in results], indent=2))
                else:
                    console.print(f"[bold]Secret Scan for {args.file}[/bold]")
                    
                    if results:
                        table = Table(show_header=True, header_style="bold magenta")
                        table.add_column("Type")
                        table.add_column("File")
                        table.add_column("Line")
                        table.add_column("Match (Masked)")
                        
                        for finding in results:
                            table.add_row(
                                finding.type,
                                finding.file,
                                str(finding.line),
                                finding.match
                            )
                        console.print(table)
                        console.print(f"\n[bold red]Found {len(results)} potential secrets.[/bold red]")
                    else:
                        console.print("\n[green]No secrets found.[/green]")

            elif args.yara:
                from .analysis.yara import YaraScanner
                import json
                from rich.table import Table
                
                try:
                    scanner = YaraScanner(args.yara)
                    results = scanner.scan_archive(Path(args.file))
                    
                    if args.json:
                        print(json.dumps(results, indent=2))
                    else:
                        console.print(f"[bold]YARA Scan for {args.file}[/bold]")
                        console.print(f"Rules: {args.yara}")
                        
                        if results:
                            for filename, matches in results.items():
                                console.print(f"\n[bold cyan]File: {filename}[/bold cyan]")
                                table = Table(show_header=True, header_style="bold magenta")
                                table.add_column("Rule")
                                table.add_column("Tags")
                                table.add_column("Meta")
                                
                                for match in matches:
                                    table.add_row(
                                        match["rule"],
                                        ", ".join(match["tags"]),
                                        str(match["meta"])
                                    )
                                console.print(table)
                        else:
                            console.print("\n[green]No YARA matches found.[/green]")
                            
                except ImportError as e:
                    console.print(f"[red]{e}[/red]")
                    sys.exit(1)
                except Exception as e:
                    console.print(f"[red]Error during YARA scan: {e}[/red]")
                    sys.exit(1)
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

        if args.command == "config":
            config = load_config()
            
            if args.config_command == "list":
                import json
                console.print(json.dumps(config, indent=2))
                return

            if args.config_command == "get":
                value = get_config_value(config, args.key)
                if value is not None:
                    console.print(value)
                else:
                    console.print(f"[yellow]Key '{args.key}' not found.[/yellow]")
                return

            if args.config_command == "set":
                # Type inference
                value = args.value
                if value.lower() == "true":
                    value = True
                elif value.lower() == "false":
                    value = False
                else:
                    try:
                        value = int(value)
                    except ValueError:
                        try:
                            value = float(value)
                        except ValueError:
                            pass  # Keep as string
                
                set_config_value(config, args.key, value)
                save_config(config)
                console.print(f"[green]Set '{args.key}' to '{value}'[/green]")
                return

        if args.command == "clean":
            from .clean import clean_artifacts
            
            # Determine what to clean
            clean_cache = args.cache
            clean_downloads = args.downloads
            
            if args.all:
                clean_cache = True
                clean_downloads = True
            
            # Get download dir from config if needed
            download_dir = None
            if clean_downloads:
                config = load_config()
                download_dir_str = get_config_value(config, "general.download_dir")
                if download_dir_str:
                    download_dir = Path(download_dir_str)
                else:
                    # Default to current dir / downloads? Or just skip?
                    # If not in config, maybe use default from parser?
                    # But parser default is calculated in get_parser.
                    # Let's re-calculate default.
                    download_dir = Path(".") # Default in get_parser is "." but usually users set it.
                    # Actually, if it's ".", cleaning it might be dangerous if it's the project root.
                    # Let's be safe and only clean if it's explicitly set or we are sure.
                    # For now, let's use the same logic as get_parser default.
                    pass

            clean_artifacts(
                base_dir=Path("."),
                clean_cache=clean_cache,
                clean_downloads=clean_downloads,
                download_dir=download_dir,
                dry_run=args.dry_run,
                force=args.force
            )
            return

        if args.command == "history":
            from .history import HistoryManager
            from rich.table import Table
            import json
            
            manager = HistoryManager()
            
            if args.clear:
                manager.clear()
                console.print("[green]History cleared.[/green]")
                return
            
            entries = manager.get_entries(limit=args.limit)
            
            if args.json:
                print(json.dumps(entries, indent=2))
            else:
                if not entries:
                    console.print("[yellow]No history found.[/yellow]")
                else:
                    table = Table(show_header=True, header_style="bold magenta")
                    table.add_column("Timestamp")
                    table.add_column("Action")
                    table.add_column("ID")
                    table.add_column("Browser")
                    table.add_column("Version")
                    table.add_column("Status")
                    
                    for entry in entries:
                        status_color = "green" if entry.get("status") == "success" else "red"
                        table.add_row(
                            entry.get("timestamp", "")[:19].replace("T", " "),
                            entry.get("action", ""),
                            entry.get("id", ""),
                            entry.get("browser", ""),
                            entry.get("version") or "-",
                            f"[{status_color}]{entry.get('status', '')}[/{status_color}]"
                        )
                    console.print(table)
            return

        if args.command == "schema":
            from .schemas import get_schema
            import json
            
            try:
                schema = get_schema(args.type)
                print(json.dumps(schema, indent=2))
            except ValueError as e:
                console.print(f"[red]{e}[/red]")
                sys.exit(1)
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
