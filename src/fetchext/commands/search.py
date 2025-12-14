from .. import core


def register(subparsers):
    # Search subcommand
    search_parser = subparsers.add_parser(
        "search", aliases=["s"], help="Search for an extension"
    )
    search_parser.add_argument(
        "browser",
        choices=["firefox", "f"],
        help="The browser type (only firefox/f supported for search)",
    )
    search_parser.add_argument("query", help="The search query")
    search_group = search_parser.add_mutually_exclusive_group()
    search_group.add_argument(
        "--json", action="store_true", help="Output results as JSON"
    )
    search_group.add_argument(
        "--csv", action="store_true", help="Output results as CSV"
    )
    search_parser.add_argument(
        "--refresh", action="store_true", help="Ignore cache and fetch fresh results"
    )
    search_parser.set_defaults(func=handle_search)


def handle_search(args, show_progress=True):
    core.search_extension(
        args.browser,
        args.query,
        json_output=args.json,
        csv_output=args.csv,
        refresh=args.refresh,
    )
