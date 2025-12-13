from pathlib import Path

def register(subparsers):
    # Graph subcommand
    graph_parser = subparsers.add_parser("graph", help="Visualize extension structure")
    graph_parser.add_argument("file", type=Path, help="Path to extension file")
    graph_parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output file path (default: <filename>_graph.html)"
    )
    graph_parser.set_defaults(func=handle_graph)

    # Timeline subcommand
    timeline_parser = subparsers.add_parser("timeline", help="Visualize file modification timeline")
    timeline_parser.add_argument("file", help="Path to the .crx or .xpi file")
    timeline_parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    timeline_parser.set_defaults(func=handle_timeline)

def handle_graph(args, show_progress=True):
    from ..analysis.graph import generate_graph
    generate_graph(args.file, args.output)

def handle_timeline(args, show_progress=True):
    from ..inspector import ExtensionInspector
    from ..console import console
    from rich.table import Table
    import json
    import sys
    
    inspector = ExtensionInspector()
    result = inspector.inspect(args.file)
    
    if result["errors"]:
        for error in result["errors"]:
            console.print(f"[red]Error: {error}[/red]")
        if not result["timeline"]:
            sys.exit(1)
            
    timeline = result["timeline"]
    
    if args.json:
        # Convert datetime objects to strings for JSON serialization
        json_timeline = []
        for item in timeline:
            item_copy = item.copy()
            item_copy["datetime"] = item_copy["datetime"].isoformat()
            json_timeline.append(item_copy)
        print(json.dumps(json_timeline, indent=2))
    else:
        console.print(f"[bold]Timeline for {args.file}[/bold]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Date/Time")
        table.add_column("File")
        table.add_column("Size")
        
        for item in timeline:
            table.add_row(
                item["datetime"].strftime("%Y-%m-%d %H:%M:%S"),
                item["filename"],
                str(item["size"])
            )
        console.print(table)
