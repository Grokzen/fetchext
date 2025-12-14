from pathlib import Path
from ..config import load_config


def register(subparsers):
    # Extract subcommand
    extract_parser = subparsers.add_parser(
        "extract", aliases=["x"], help="Extract extension contents"
    )
    extract_parser.add_argument("file", type=Path, help="Path to extension file")
    extract_parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        help="Output directory (default: <filename>_extracted)",
    )
    extract_parser.set_defaults(func=handle_extract)

    # Tutorial subcommand
    tutorial_parser = subparsers.add_parser("tutorial", help="Run interactive tutorial")
    tutorial_parser.set_defaults(func=handle_tutorial)

    # Optimize subcommand
    optimize_parser = subparsers.add_parser(
        "optimize", help="Optimize images in an extension"
    )
    optimize_parser.add_argument(
        "directory", type=Path, help="Path to the extension directory"
    )
    optimize_parser.add_argument(
        "-q",
        "--quality",
        type=int,
        default=85,
        help="Image quality (1-100, default: 85)",
    )
    optimize_parser.add_argument(
        "--json", action="store_true", help="Output results as JSON"
    )
    optimize_parser.set_defaults(func=handle_optimize)

    # Clean subcommand
    clean_parser = subparsers.add_parser("clean", help="Clean up caches and artifacts")
    clean_parser.add_argument(
        "--cache",
        action="store_true",
        default=True,
        help="Clean build and test caches (default)",
    )
    clean_parser.add_argument(
        "--downloads", action="store_true", help="Clean download directory"
    )
    clean_parser.add_argument("--all", action="store_true", help="Clean everything")
    clean_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without deleting",
    )
    clean_parser.add_argument(
        "-f", "--force", action="store_true", help="Skip confirmation"
    )
    clean_parser.set_defaults(func=handle_clean)

    # Schema subcommand
    schema_parser = subparsers.add_parser("schema", help="Get JSON schema for outputs")
    schema_parser.add_argument(
        "type",
        choices=["config", "audit", "risk", "history", "scan"],
        help="The type of schema to generate",
    )
    schema_parser.set_defaults(func=handle_schema)

    # Convert subcommand
    convert_parser = subparsers.add_parser("convert", help="Convert extension format")
    convert_parser.add_argument("input", help="Input file or directory")
    convert_parser.add_argument(
        "--to", choices=["zip"], default="zip", help="Target format (default: zip)"
    )
    convert_parser.add_argument("-o", "--output", type=Path, help="Output file path")
    convert_parser.set_defaults(func=handle_convert)


def handle_extract(args, show_progress=True):
    from ..core import extract_extension

    extract_extension(args.file, args.output_dir)


def handle_tutorial(args, show_progress=True):
    from ..tutorial import run_tutorial

    run_tutorial()


def handle_optimize(args, show_progress=True):
    from ..optimizer import optimize_extension
    from ..console import console
    import json

    results = optimize_extension(args.directory, quality=args.quality)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        console.print(f"[bold]Optimization Results for {args.directory}[/bold]")
        console.print(f"Total Files: {results['total_files']}")
        console.print(f"Optimized Files: {results['optimized_files']}")
        console.print(f"Original Size: {results['original_size'] / 1024:.2f} KB")
        console.print(f"New Size: {results['new_size'] / 1024:.2f} KB")
        console.print(
            f"Saved: {results['saved_bytes'] / 1024:.2f} KB ({(results['saved_bytes'] / results['original_size'] * 100) if results['original_size'] > 0 else 0:.1f}%)"
        )


def handle_clean(args, show_progress=True):
    from ..clean import clean_artifacts
    from ..config import get_config_value

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
            download_dir = Path(".")

    clean_artifacts(
        base_dir=Path("."),
        clean_cache=clean_cache,
        clean_downloads=clean_downloads,
        download_dir=download_dir,
        dry_run=args.dry_run,
        force=args.force,
    )


def handle_schema(args, show_progress=True):
    from ..schemas import get_schema
    from ..console import console
    import json
    import sys

    try:
        schema = get_schema(args.type)
        print(json.dumps(schema, indent=2))
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)


def handle_convert(args, show_progress=True):
    from ..core import convert_extension

    convert_extension(args.input, args.output, to_format=args.to)
