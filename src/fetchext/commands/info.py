from pathlib import Path


def register(subparsers):
    # Info subcommand
    info_parser = subparsers.add_parser("info", help="Show extension metadata")
    info_parser.add_argument("file", type=Path, help="Path to extension file")
    info_parser.add_argument("--json", action="store_true", help="Output as JSON")
    info_parser.set_defaults(func=handle_info)

    # Explain subcommand
    explain_parser = subparsers.add_parser("explain", help="Explain a permission")
    explain_parser.add_argument("permission", help="The permission string to explain")
    explain_parser.add_argument(
        "--json", action="store_true", help="Output results as JSON"
    )
    explain_parser.set_defaults(func=handle_explain)

    # History subcommand
    history_parser = subparsers.add_parser("history", help="View download history")
    history_parser.add_argument(
        "--limit", type=int, default=20, help="Number of entries to show (default: 20)"
    )
    history_parser.add_argument(
        "--clear", action="store_true", help="Clear the history"
    )
    history_parser.add_argument(
        "--json", action="store_true", help="Output results as JSON"
    )
    history_parser.set_defaults(func=handle_history)

    # Stats subcommand
    stats_parser = subparsers.add_parser("stats", help="Analyze repository statistics")
    stats_parser.add_argument(
        "directory",
        type=Path,
        nargs="?",
        default=Path("."),
        help="Directory to scan (default: current directory)",
    )
    stats_parser.add_argument(
        "--json", action="store_true", help="Output results as JSON"
    )
    stats_parser.set_defaults(func=handle_stats)


def handle_info(args, show_progress=True):
    from fetchext.security.inspector  import show_info

    show_info(args.file, as_json=args.json)


def handle_explain(args, show_progress=True):
    from fetchext.analysis .explainer import explain_permission
    from fetchext.interface.console  import console
    import json
    from rich.panel import Panel

    result = explain_permission(args.permission)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result:
            risk_color = {
                "Low": "green",
                "Medium": "yellow",
                "High": "red",
                "Critical": "bold red",
            }.get(result["risk"], "white")

            console.print(
                Panel(
                    f"[bold]Description:[/bold] {result['description']}\n\n"
                    f"[bold]Risk Level:[/bold] [{risk_color}]{result['risk']}[/{risk_color}]",
                    title=f"[bold cyan]{args.permission}[/bold cyan]",
                    expand=False,
                )
            )
        else:
            console.print(
                f"[red]Permission '{args.permission}' not found in database.[/red]"
            )


def handle_history(args, show_progress=True):
    from fetchext.data.history  import HistoryManager
    from fetchext.interface.console  import console
    from rich.table import Table
    import json

    manager = HistoryManager()

    if args.clear:
        manager.clear()
        console.print("[green]History cleared.[/green]")
        return

    entries = manager.get_entries(limit=args.limit)

    if args.json:
        print(json.dumps(entries, indent=2))
    else:
        if not entries:
            console.print("[yellow]No history found.[/yellow]")
        else:
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Timestamp")
            table.add_column("Action")
            table.add_column("ID")
            table.add_column("Browser")
            table.add_column("Version")
            table.add_column("Status")

            for entry in entries:
                status_color = "green" if entry.get("status") == "success" else "red"
                table.add_row(
                    entry.get("timestamp", "")[:19].replace("T", " "),
                    entry.get("action", ""),
                    entry.get("id", ""),
                    entry.get("browser", ""),
                    entry.get("version") or "-",
                    f"[{status_color}]{entry.get('status', '')}[/{status_color}]",
                )
            console.print(table)


def handle_stats(args, show_progress=True):
    from fetchext.core.core  import get_repo_stats

    get_repo_stats(args.directory, json_output=args.json)
