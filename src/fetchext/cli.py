import sys
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime, timezone
from rich.logging import RichHandler
from .downloaders import ChromeDownloader, EdgeDownloader, FirefoxDownloader
from .inspector import ExtensionInspector
from .batch import BatchProcessor
from .console import console
from .utils import open_extension_archive
from .config import load_config

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

    # Inspect subcommand
    inspect_parser = subparsers.add_parser("inspect", aliases=["i"], help="Inspect an extension file")
    inspect_parser.add_argument("file", help="Path to the .crx or .xpi file")

    # Extract subcommand
    extract_parser = subparsers.add_parser("extract", aliases=["x"], help="Extract an extension file")
    extract_parser.add_argument("file", help="Path to the .crx or .xpi file")
    extract_parser.add_argument(
        "-o", "--output-dir",
        type=Path,
        help="Directory to extract to (default: <filename_stem> in current dir)"
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
        # Also set root logger or handler level if needed, but basicConfig set handler
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
            inspector = ExtensionInspector()
            inspector.inspect(args.file)
            if not args.quiet:
                logger.info("Inspection finished successfully.")
            return

        if args.command in ["extract", "x"]:
            file_path = Path(args.file)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            if args.output_dir:
                extract_dir = args.output_dir
            else:
                extract_dir = Path(".") / file_path.stem
                
            if extract_dir.exists() and any(extract_dir.iterdir()):
                 logger.warning(f"Extraction directory {extract_dir} is not empty.")
            
            extract_dir.mkdir(parents=True, exist_ok=True)
            
            if not args.quiet:
                logger.info(f"Extracting {file_path} to {extract_dir}...")
            try:
                with open_extension_archive(file_path) as zf:
                    zf.extractall(extract_dir)
                if not args.quiet:
                    logger.info("Extraction finished successfully.")
            except Exception as e:
                logger.error(f"Extraction failed: {e}")
            return

        if args.command in ["batch", "b"]:
            processor = BatchProcessor()
            processor.process(args.file, args.output_dir, max_workers=args.workers, show_progress=show_progress)
            if not args.quiet:
                logger.info("Batch processing finished successfully.")
            return

        downloader = None
        if args.browser in ["chrome", "c"]:
            downloader = ChromeDownloader()
        elif args.browser in ["edge", "e"]:
            downloader = EdgeDownloader()
        elif args.browser in ["firefox", "f"]:
            downloader = FirefoxDownloader()

        if not downloader:
            raise ValueError("Unsupported browser type")

        if args.command in ["download", "d"]:
            extension_id = downloader.extract_id(args.url)
            if not args.quiet:
                logger.info(f"Extracted ID/Slug: {extension_id}")

            output_dir = args.output_dir
            if not output_dir.exists():
                output_dir.mkdir(parents=True, exist_ok=True)

            output_path = downloader.download(extension_id, output_dir, show_progress=show_progress)
            
            if args.save_metadata:
                if not args.quiet:
                    logger.info("Generating metadata sidecar...")
                try:
                    inspector = ExtensionInspector()
                    manifest = inspector.get_manifest(output_path)
                    
                    metadata = {
                        "id": extension_id,
                        "name": manifest.get("name", "Unknown"),
                        "version": manifest.get("version", "Unknown"),
                        "source_url": args.url,
                        "download_timestamp": datetime.now(timezone.utc).isoformat(),
                        "filename": output_path.name
                    }
                    
                    # Save as <filename>.json (e.g. extension.crx.json)
                    metadata_path = output_path.with_suffix(output_path.suffix + ".json")
                    
                    with open(metadata_path, "w") as f:
                        json.dump(metadata, f, indent=2)
                        
                    if not args.quiet:
                        logger.info(f"Metadata saved to {metadata_path}")
                except Exception as e:
                    logger.warning(f"Failed to generate metadata: {e}")

            if args.extract:
                if not args.quiet:
                    logger.info("Extracting extension...")
                try:
                    # Determine extract directory
                    # Use filename stem (e.g. ublock_origin-1.68.0)
                    extract_dir = output_dir / output_path.stem
                    if extract_dir.exists():
                        logger.warning(f"Extraction directory {extract_dir} already exists. Overwriting...")
                    
                    extract_dir.mkdir(parents=True, exist_ok=True)
                    
                    with open_extension_archive(output_path) as zf:
                        zf.extractall(extract_dir)
                        
                    if not args.quiet:
                        logger.info(f"Successfully extracted to {extract_dir}")
                except Exception as e:
                    logger.error(f"Failed to extract extension: {e}")

        elif args.command in ["search", "s"]:
            if not hasattr(downloader, 'search'):
                 raise ValueError(f"Search not supported for {args.browser}")
            downloader.search(args.query)

        if not args.quiet:
            logger.info("Script finished successfully.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
