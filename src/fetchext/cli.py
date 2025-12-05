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

def main():
    """
    Main entry point of the script.
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
    search_parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
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

        if args.command in ["batch", "b"]:
            core.batch_download(args.file, args.output_dir, workers=args.workers, show_progress=show_progress)
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
            core.search_extension(args.browser, args.query, json_output=args.json)

        if not args.quiet:
            logger.info("Script finished successfully.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
