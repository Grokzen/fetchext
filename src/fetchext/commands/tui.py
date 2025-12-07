
def register(subparsers):
    # UI subcommand
    ui_parser = subparsers.add_parser("ui", help="Launch TUI")
    ui_parser.set_defaults(func=handle_ui)

def handle_ui(args, show_progress=True):
    from ..tui import run_tui
    run_tui()
