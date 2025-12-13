
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

    # Config Remote
    remote_parser = config_subparsers.add_parser("remote", help="Load configuration from a remote URL")
    remote_parser.add_argument("url", help="URL to the TOML config file")
    remote_parser.set_defaults(func=handle_config_remote)

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

def handle_config_remote(args, show_progress=True):
    import requests
    import tomli_w
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib
    from ..config import get_config_path
    from ..console import console
    from ..constants import ExitCode

    url = args.url
    console.print(f"Fetching config from {url}...")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Validate TOML
        new_config = tomllib.loads(response.text)
        
        # Save
        config_path = get_config_path()
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, "wb") as f:
            tomli_w.dump(new_config, f)
            
        console.print("[green]Configuration updated from remote URL.[/green]")
        console.print(f"Saved to: {config_path}")

    except requests.RequestException as e:
        console.print(f"[red]Failed to fetch config: {e}[/red]")
        raise SystemExit(ExitCode.NETWORK)
    except tomllib.TOMLDecodeError as e:
        console.print(f"[red]Invalid TOML content: {e}[/red]")
        raise SystemExit(ExitCode.CONFIG)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise SystemExit(ExitCode.ERROR)

def handle_setup(args, show_progress=True):
    from ..setup import run_setup
    run_setup()
