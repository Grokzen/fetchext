from ..core import share_report


def register(subparsers):
    parser = subparsers.add_parser(
        "share", help="Share a report via Gist or other providers."
    )
    parser.add_argument("file", help="Path to the report file to share.")
    parser.add_argument(
        "--provider",
        choices=["gist"],
        default=None,
        help="Sharing provider (default: gist).",
    )
    parser.add_argument("--description", help="Description for the shared file.")
    parser.set_defaults(func=handle_share)


def handle_share(args, show_progress=True):
    """
    Handle the share command.
    """
    try:
        share_report(args.file, provider=args.provider, description=args.description)
    except Exception:
        # Error is already logged/printed in core.share_report or caught in main
        raise
