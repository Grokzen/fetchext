from ..watcher import DirectoryWatcher

def register(subparsers):
    parser = subparsers.add_parser("watch", help="Monitor a directory for new extensions.")
    parser.add_argument("directory", help="Directory to watch.")
    parser.add_argument("--extract", action="store_true", help="Automatically extract new extensions.")
    parser.add_argument("--report", action="store_true", help="Automatically generate reports.")
    parser.add_argument("--scan", action="store_true", help="Automatically scan for vulnerabilities.")
    parser.set_defaults(func=handle_watch)

def handle_watch(args, show_progress=True):
    """
    Handle the watch command.
    """
    actions = []
    if args.extract:
        actions.append("extract")
    if args.report:
        actions.append("report")
    if args.scan:
        actions.append("scan")
        
    watcher = DirectoryWatcher(args.directory, actions=actions)
    watcher.start()
