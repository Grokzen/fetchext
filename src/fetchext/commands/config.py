
def register(subparsers):
    # Config subcommand
    config_parser = subparsers.add_parser("config", help="Manage configuration")
    config_subparsers = config_parser.add_subparsers(dest="config_command", required=True)

    # Config Show
    show_parser = config_subparsers.add_parser("show", help="Show current configuration")
    show_parser.set_defaults(func=handle_config_show)

    # Config Init
    init_parser = config_subparsers.add_parser("init", help="Initialize default configuration")
    init_parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Overwrite existing configuration"
    )
    init_parser.set_defaults(func=handle_config_init)

    # Setup subcommand
    setup_parser = subparsers.add_parser("setup", help="Run configuration wizard")
    setup_parser.set_defaults(func=handle_setup)

def handle_config_show(args, show_progress=True):
    from ..config import load_config
    import tomli_w
    config = load_config()
    print(tomli_w.dumps(config))

def handle_config_init(args, show_progress=True):
    from ..config import create_default_config
    create_default_config(force=args.force)

def handle_setup(args, show_progress=True):
    from ..setup import run_setup
    run_setup()
