import sys
import logging
import argparse
from pathlib import Path
from rich.logging import RichHandler
from .downloaders import ChromeDownloader, EdgeDownloader, FirefoxDownloader
from .inspector import ExtensionInspector
from .batch import BatchProcessor
from .console import console

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
    parser = argparse.ArgumentParser(description="Download or search for browser extensions.")
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
        default=Path("."),
        help="Directory to save the downloaded extension"
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

    # Batch subcommand
    batch_parser = subparsers.add_parser("batch", aliases=["b"], help="Download extensions from a batch file")
    batch_parser.add_argument("file", help="Path to the batch file containing URLs")
    batch_parser.add_argument(
        "-o", "--output-dir",
        type=Path,
        default=Path("."),
        help="Directory to save the downloaded extensions"
    )
    batch_parser.add_argument(
        "-w", "--workers",
        type=int,
        default=4,
        help="Number of parallel workers (default: 4)"
    )

    args = parser.parse_args()

    logger.info("Starting fetchext...")

    try:
        if args.command in ["inspect", "i"]:
            inspector = ExtensionInspector()
            inspector.inspect(args.file)
            logger.info("Inspection finished successfully.")
            return

        if args.command in ["batch", "b"]:
            processor = BatchProcessor()
            processor.process(args.file, args.output_dir, max_workers=args.workers)
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
            logger.info(f"Extracted ID/Slug: {extension_id}")

            output_dir = args.output_dir
            if not output_dir.exists():
                output_dir.mkdir(parents=True, exist_ok=True)

            downloader.download(extension_id, output_dir)
        elif args.command in ["search", "s"]:
            if not hasattr(downloader, 'search'):
                 raise ValueError(f"Search not supported for {args.browser}")
            downloader.search(args.query)

        logger.info("Script finished successfully.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
