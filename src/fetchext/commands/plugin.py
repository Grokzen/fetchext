def register(subparsers):
    # Plugin subcommand
    plugin_parser = subparsers.add_parser("plugin", help="Manage plugins")
    plugin_subparsers = plugin_parser.add_subparsers(
        dest="plugin_command", required=True, help="Plugin action"
    )

    plugin_subparsers.add_parser("list", help="List installed plugins")

    enable_parser = plugin_subparsers.add_parser("enable", help="Enable a plugin")
    enable_parser.add_argument("name", help="Plugin name")

    disable_parser = plugin_subparsers.add_parser("disable", help="Disable a plugin")
    disable_parser.add_argument("name", help="Plugin name")

    install_parser = plugin_subparsers.add_parser("install", help="Install a plugin")
    install_parser.add_argument("path", help="Path to plugin file")

    remove_parser = plugin_subparsers.add_parser("remove", help="Remove a plugin")
    remove_parser.add_argument("name", help="Plugin name")

    plugin_parser.set_defaults(func=handle_plugin)


def handle_plugin(args, show_progress=True):
    from fetchext.plugins.manager  import PluginManager
    from fetchext.interface.console  import console
    from rich.table import Table
    import sys

    manager = PluginManager()

    if args.plugin_command == "list":
        plugins = manager.list_plugins()
        if not plugins:
            console.print("[yellow]No plugins installed.[/yellow]")
        else:
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Name")
            table.add_column("Status")
            table.add_column("File")

            for p in plugins:
                status_color = "green" if p["status"] == "enabled" else "red"
                table.add_row(
                    p["name"],
                    f"[{status_color}]{p['status']}[/{status_color}]",
                    p["file"],
                )
            console.print(table)
        return

    try:
        if args.plugin_command == "enable":
            manager.enable_plugin(args.name)
            console.print(f"[green]Plugin '{args.name}' enabled.[/green]")
        elif args.plugin_command == "disable":
            manager.disable_plugin(args.name)
            console.print(f"[yellow]Plugin '{args.name}' disabled.[/yellow]")
        elif args.plugin_command == "install":
            name = manager.install_plugin(args.path)
            console.print(f"[green]Plugin '{name}' installed.[/green]")
        elif args.plugin_command == "remove":
            manager.remove_plugin(args.name)
            console.print(f"[green]Plugin '{args.name}' removed.[/green]")
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)
