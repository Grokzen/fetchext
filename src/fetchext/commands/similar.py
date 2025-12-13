from pathlib import Path
from ..analysis.similarity import SimilarityEngine
from ..console import console
from ..config import load_config

def register(subparsers):
    parser = subparsers.add_parser("similar", help="Find similar extensions")
    parser.add_argument("file", help="Target extension file")
    parser.add_argument(
        "-t", "--threshold",
        type=int,
        default=50,
        help="Minimum similarity score (0-100)"
    )
    parser.add_argument(
        "-d", "--dir",
        type=Path,
        help="Directory to search (default: configured download dir)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    parser.set_defaults(func=handle_similar)

def handle_similar(args, show_progress=True):
    target_path = Path(args.file)
    if not target_path.exists():
        console.print(f"[red]File not found: {target_path}[/red]")
        return

    config = load_config()
    repo_dir = args.dir if args.dir else Path(config["download"]["directory"])
    
    if not repo_dir.exists():
        console.print(f"[red]Repository directory not found: {repo_dir}[/red]")
        return

    engine = SimilarityEngine()
    
    if show_progress:
        console.print(f"Computing hash for {target_path}...")
        
    matches = engine.find_similar(target_path, repo_dir, threshold=args.threshold)
    
    if args.json:
        console.print_json(data=matches)
    else:
        console.print(f"[bold]Similarity Search Results for {target_path.name}[/bold]")
        console.print(f"Searching in: {repo_dir}")
        console.print(f"Threshold: {args.threshold}\n")
        
        if matches:
            from rich.table import Table
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("File")
            table.add_column("Score")
            table.add_column("Hash (Truncated)")
            
            for match in matches:
                table.add_row(
                    Path(match["file"]).name,
                    str(match["score"]),
                    match["hash"][:20] + "..."
                )
            console.print(table)
        else:
            console.print("[yellow]No similar extensions found.[/yellow]")
