import sys
import csv
from ..history import HistoryManager
from ..console import console
from rich.table import Table

def register(subparsers):
    parser = subparsers.add_parser("query", help="Execute SQL query against history database")
    parser.add_argument("sql", help="SQL query to execute")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--csv", action="store_true", help="Output as CSV")
    parser.set_defaults(func=handle_query)

def handle_query(args, show_progress=True):
    history = HistoryManager()
    try:
        results = history.execute_query(args.sql)
        
        if not results:
            if not args.json and not args.csv:
                console.print("No results or query executed successfully.")
            return

        if args.json:
            console.print_json(data=results)
        elif args.csv:
            writer = csv.writer(sys.stdout)
            if results:
                header = results[0].keys()
                writer.writerow(header)
                for row in results:
                    writer.writerow(row.values())
        else:
            # Rich Table
            table = Table(show_header=True, header_style="bold magenta")
            if results:
                columns = results[0].keys()
                for col in columns:
                    table.add_column(col)
                
                for row in results:
                    table.add_row(*[str(v) for v in row.values()])
            
            console.print(table)
            console.print(f"\n[dim]{len(results)} rows returned[/dim]")
            
    except Exception as e:
        console.print_error(f"Query failed: {e}")
        sys.exit(1)
