from pathlib import Path
from fetchext.core import core
from fetchext.data.config  import load_config


def register(subparsers):
    config = load_config()
    general_config = config.get("general", {})
    batch_config = config.get("batch", {})

    default_output_dir = Path(general_config.get("download_dir", "."))
    default_workers = batch_config.get("workers", 4)
    default_save_metadata = general_config.get("save_metadata", False)
    default_extract = general_config.get("extract", False)

    # Download subcommand
    download_parser = subparsers.add_parser(
        "download", aliases=["d"], help="Download an extension"
    )
    download_parser.add_argument(
        "browser",
        choices=["chrome", "c", "edge", "e", "firefox", "f"],
        help="The browser type (chrome/c, edge/e, firefox/f)",
    )
    download_parser.add_argument(
        "url", help="The URL of the extension in the Web Store"
    )
    download_parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=default_output_dir,
        help=f"Directory to save the downloaded extension (default: {default_output_dir})",
    )
    download_parser.add_argument(
        "-m",
        "--save-metadata",
        action="store_true",
        default=default_save_metadata,
        help="Save metadata to a JSON file alongside the extension",
    )
    download_parser.add_argument(
        "-x",
        "--extract",
        action="store_true",
        default=default_extract,
        help="Automatically extract the extension to a folder",
    )
    download_parser.add_argument(
        "--verify-hash",
        metavar="SHA256",
        help="Verify the downloaded file against this SHA256 hash",
    )
    download_parser.set_defaults(func=handle_download)

    # Batch subcommand
    batch_parser = subparsers.add_parser(
        "batch", aliases=["b"], help="Download extensions from a batch file"
    )
    batch_parser.add_argument("file", help="Path to the batch file containing URLs")
    batch_parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=default_output_dir,
        help=f"Directory to save the downloaded extensions (default: {default_output_dir})",
    )
    batch_parser.add_argument(
        "-w",
        "--workers",
        type=int,
        default=default_workers,
        help=f"Number of parallel workers (default: {default_workers})",
    )
    batch_parser.set_defaults(func=handle_batch)


def handle_download(args, show_progress=True):
    core.download_extension(
        args.browser,
        args.url,
        args.output_dir,
        save_metadata=args.save_metadata,
        extract=args.extract,
        show_progress=show_progress,
        verify_hash=args.verify_hash,
    )


def handle_batch(args, show_progress=True):
    core.batch_download(
        args.file, args.output_dir, workers=args.workers, show_progress=show_progress
    )
