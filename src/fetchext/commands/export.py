import sys
from pathlib import Path
from fetchext.interface.console  import console
from fetchext.core import core


def register(subparsers):
    parser = subparsers.add_parser(
        "export", help="Export analysis data to external formats"
    )
    parser.add_argument(
        "file", type=Path, help="Path to the extension file or directory"
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--stix", action="store_true", help="Export as STIX 2.1 Bundle (JSON)"
    )

    parser.add_argument(
        "-o", "--output", type=Path, help="Output file path (default: stdout)"
    )
    parser.set_defaults(func=handle_export)


def handle_export(args, show_progress=True):
    if args.stix:
        from fetchext.analysis .stix import StixGenerator

        # We need to gather analysis data first
        # This might be expensive if we run everything
        # For now, let's run a basic analysis

        console.print(
            f"[bold blue]Gathering analysis data for {args.file}...[/bold blue]"
        )

        # Use core.generate_unified_report to get all data
        # This includes domains, hashes, yara, etc.
        report = core.generate_unified_report(args.file)

        try:
            generator = StixGenerator(args.file)
            stix_json = generator.generate(report)

            if args.output:
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(stix_json)
                console.print(f"[green]STIX bundle saved to {args.output}[/green]")
            else:
                console.print(stix_json)

        except Exception as e:
            console.print(f"[red]Export failed: {e}[/red]")
            sys.exit(1)
