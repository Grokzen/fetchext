from pathlib import Path
from ..config import load_config

def register(subparsers):
    config = load_config()
    general_config = config.get("general", {})
    batch_config = config.get("batch", {})
    default_output_dir = Path(general_config.get("download_dir", "."))
    default_workers = batch_config.get("workers", 4)

    # Serve subcommand
    serve_parser = subparsers.add_parser("serve", help="Host local repository as update server")
    serve_parser.add_argument(
        "-d", "--directory",
        type=Path,
        default=Path("."),
        help="Directory to serve (default: current directory)"
    )
    serve_parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)"
    )
    serve_parser.add_argument(
        "-p", "--port",
        type=int,
        default=8000,
        help="Port to listen on (default: 8000)"
    )
    serve_parser.set_defaults(func=handle_serve)

    # Update Manifest subcommand
    manifest_parser = subparsers.add_parser("update-manifest", aliases=["um"], help="Generate update manifest for local extensions")
    manifest_parser.add_argument("directory", type=Path, help="Directory containing extension files")
    manifest_parser.add_argument("--base-url", required=True, help="Base URL where extensions are hosted")
    manifest_parser.add_argument("--output", type=Path, help="Output file path (optional)")
    manifest_parser.set_defaults(func=handle_update_manifest)

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
    mirror_parser.set_defaults(func=handle_mirror)

def handle_serve(args, show_progress=True):
    from ..server import run_server
    run_server(args.directory, args.host, args.port)

def handle_update_manifest(args, show_progress=True):
    from ..server import generate_update_manifest
    generate_update_manifest(args.directory, args.base_url, args.output)

def handle_mirror(args, show_progress=True):
    from ..mirror import MirrorManager
    manager = MirrorManager()
    manager.sync(args.list_file, args.output_dir, prune=args.prune, workers=args.workers, show_progress=show_progress)
