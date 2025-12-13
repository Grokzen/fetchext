import logging
from pathlib import Path
from fetchext.migration import MV3Migrator
from fetchext.console import console

logger = logging.getLogger(__name__)

def register(subparsers):
    parser = subparsers.add_parser("migrate", help="Migrate an MV2 extension to MV3")
    add_arguments(parser)
    parser.set_defaults(func=lambda args, **kwargs: handle_migrate(args))

def add_arguments(parser):
    parser.add_argument("directory", help="Directory containing the extension source code")
    parser.add_argument("--dry-run", action="store_true", help="Simulate migration without modifying files")

def handle_migrate(args):
    source_dir = Path(args.directory)
    if not source_dir.exists() or not source_dir.is_dir():
        console.print(f"[bold red]Error:[/bold red] Directory not found: {source_dir}")
        return 1

    migrator = MV3Migrator(source_dir)
    try:
        report = migrator.migrate(dry_run=args.dry_run)
        
        console.print("[bold]Migration Report[/bold]")
        
        if report.changes:
            console.print("\n[bold green]Changes Applied:[/bold green]")
            for change in report.changes:
                console.print(f"  + {change}")
                
        if report.warnings:
            console.print("\n[bold yellow]Warnings (Manual Action Required):[/bold yellow]")
            for warning in report.warnings:
                console.print(f"  ! {warning}")
                
        if report.errors:
            console.print("\n[bold red]Errors:[/bold red]")
            for error in report.errors:
                console.print(f"  x {error}")
                
        if args.dry_run:
            console.print("\n[dim]Dry run completed. No files were modified.[/dim]")
        else:
            console.print("\n[bold green]Migration completed.[/bold green]")
            
    except Exception as e:
        console.print(f"[bold red]Migration failed:[/bold red] {e}")
        logger.exception("Migration failed")
        return 1
        
    return 0
