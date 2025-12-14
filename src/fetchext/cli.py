import sys
import logging
import argparse
from importlib.metadata import version, PackageNotFoundError
from rich.logging import RichHandler
from .console import console
from .exceptions import FetchextError
from .constants import ExitCode
from .commands import (
    download,
    search,
    inspect,
    audit,
    server,
    utils,
    config,
    info,
    visualize,
    tui,
    plugin,
    beautify,
    similar,
    pack,
    migrate,
    git,
    update,
    badge,
    grep,
    sandbox,
    share,
    watch,
    query,
    export,
    rules
)

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
    parser = argparse.ArgumentParser(description="Download or search for browser extensions.")
    
    try:
        ver = version("fetchext")
    except PackageNotFoundError:
        ver = "unknown"

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {ver}"
    )
    
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

    # Register commands from modules
    download.register(subparsers)
    search.register(subparsers)
    inspect.register(subparsers)
    audit.register(subparsers)
    server.register(subparsers)
    utils.register(subparsers)
    config.register(subparsers)
    info.register(subparsers)
    visualize.register(subparsers)
    tui.register(subparsers)
    plugin.register(subparsers)
    beautify.register(subparsers)
    similar.register(subparsers)
    pack.register(subparsers)
    migrate.register(subparsers)
    git.register(subparsers)
    update.register(subparsers)
    badge.register(subparsers)
    grep.register(subparsers)
    sandbox.register(subparsers)
    share.register(subparsers)
    watch.register(subparsers)
    query.register(subparsers)
    export.register(subparsers)
    rules.register(subparsers)

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
        if hasattr(args, "func"):
            args.func(args, show_progress=show_progress)
        else:
            parser.print_help()
            sys.exit(ExitCode.USAGE)

        if not args.quiet:
            logger.info("Script finished successfully.")
        sys.exit(ExitCode.SUCCESS)

    except FetchextError as e:
        # Handle known errors gracefully
        if args.verbose:
            logger.exception(e)
        else:
            logger.error(str(e))
        sys.exit(e.exit_code)

    except KeyboardInterrupt:
        logger.error("Operation cancelled by user.")
        sys.exit(ExitCode.CANCELLED)

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        if args.verbose:
            logger.exception(e)
        sys.exit(ExitCode.ERROR)

if __name__ == "__main__":
    main()
