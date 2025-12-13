import sys
from pathlib import Path
from .. import core
from ..console import console

def register(subparsers):
    # Audit subcommand
    audit_parser = subparsers.add_parser("audit", aliases=["a"], help="Audit extension for MV3 compatibility")
    audit_parser.add_argument("file", help="Path to the .crx or .xpi file")
    audit_parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    audit_parser.set_defaults(func=handle_audit)

    # Risk subcommand
    risk_parser = subparsers.add_parser("risk", aliases=["r"], help="Analyze permission risk")
    risk_parser.add_argument("file", help="Path to the .crx or .xpi file")
    risk_parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    risk_parser.set_defaults(func=handle_risk)

    # Scan subcommand
    scan_parser = subparsers.add_parser("scan", help="Scan extension for vulnerable dependencies")
    scan_parser.add_argument("file", help="Path to the .crx or .xpi file")
    scan_group = scan_parser.add_mutually_exclusive_group()
    scan_group.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    scan_group.add_argument(
        "--csv",
        action="store_true",
        help="Output results as CSV"
    )
    scan_parser.set_defaults(func=handle_scan)

    # Analyze subcommand
    analyze_parser = subparsers.add_parser("analyze", help="Analyze extension code")
    analyze_subparsers = analyze_parser.add_subparsers(dest="analysis_type", required=True, help="Type of analysis")

    # Complexity
    complexity_parser = analyze_subparsers.add_parser("complexity", help="Calculate cyclomatic complexity")
    complexity_parser.add_argument("file", help="Path to the .crx or .xpi file")
    complexity_parser.add_argument("--json", action="store_true", help="Output results as JSON")

    # Entropy
    entropy_parser = analyze_subparsers.add_parser("entropy", help="Calculate entropy")
    entropy_parser.add_argument("file", help="Path to the .crx or .xpi file")
    entropy_parser.add_argument("--json", action="store_true", help="Output results as JSON")

    # Domains
    domains_parser = analyze_subparsers.add_parser("domains", help="Extract domains and URLs")
    domains_parser.add_argument("file", help="Path to the .crx or .xpi file")
    domains_parser.add_argument("--json", action="store_true", help="Output results as JSON")

    # Secrets
    secrets_parser = analyze_subparsers.add_parser("secrets", help="Scan for potential secrets")
    secrets_parser.add_argument("file", help="Path to the .crx or .xpi file")
    secrets_parser.add_argument("--json", action="store_true", help="Output results as JSON")

    # Yara
    yara_parser = analyze_subparsers.add_parser("yara", help="Scan against YARA rules")
    yara_parser.add_argument("rules", type=Path, help="Path to YARA rules file or directory")
    yara_parser.add_argument("file", help="Path to the .crx or .xpi file")
    yara_parser.add_argument("--json", action="store_true", help="Output results as JSON")

    analyze_parser.set_defaults(func=handle_analyze)

    # Report subcommand
    report_parser = subparsers.add_parser("report", help="Generate a comprehensive report")
    report_parser.add_argument("file", help="Path to the .crx or .xpi file")
    report_parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output file path (default: <filename>_REPORT.md for markdown, stdout for JSON)"
    )
    report_parser.add_argument(
        "--json",
        action="store_true",
        help="Output unified report as JSON"
    )
    report_parser.add_argument(
        "--yara",
        type=Path,
        help="Path to YARA rules file or directory (optional, for JSON report)"
    )
    report_parser.set_defaults(func=handle_report)

def handle_audit(args, show_progress=True):
    core.audit_extension(args.file, json_output=args.json)

def handle_risk(args, show_progress=True):
    core.analyze_risk(args.file, json_output=args.json)

def handle_scan(args, show_progress=True):
    core.scan_extension(args.file, json_output=args.json, csv_output=args.csv)

def handle_report(args, show_progress=True):
    if args.json:
        report = core.generate_unified_report(args.file, yara_rules=args.yara)
        if args.output:
            import json
            with args.output.open("w") as f:
                json.dump(report, f, indent=2)
            if show_progress:
                console.print(f"JSON report saved to {args.output}")
        else:
            console.print_json(data=report)
    else:
        core.generate_report(args.file, args.output)

def handle_analyze(args, show_progress=True):
    if args.analysis_type == "complexity":
        from ..analysis.complexity import analyze_complexity
        from rich.table import Table
        
        results = analyze_complexity(Path(args.file), show_progress=show_progress)
        
        if args.json:
            console.print_json(data=results)
        else:
            console.print(f"[bold]Complexity Analysis for {args.file}[/bold]")
            console.print(f"Average Complexity: {results['average_complexity']:.2f}")
            console.print(f"Max Complexity: {results['max_complexity']}")
            console.print(f"Total Functions: {results['total_functions']}")
            
            if results["high_complexity_functions"]:
                console.print("\n[bold red]High Complexity Functions (>15):[/bold red]")
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("File")
                table.add_column("Function")
                table.add_column("Complexity")
                table.add_column("Length")
                
                for func in results["high_complexity_functions"]:
                    table.add_row(
                        func["file"],
                        func["function"],
                        str(func["complexity"]),
                        str(func["length"])
                    )
                console.print(table)
            else:
                console.print("\n[green]No high complexity functions found.[/green]")
    
    elif args.analysis_type == "entropy":
        from ..analysis.entropy import analyze_entropy
        from rich.table import Table
        
        results = analyze_entropy(Path(args.file), show_progress=show_progress)
        
        if args.json:
            console.print_json(data=results)
        else:
            console.print(f"[bold]Entropy Analysis for {args.file}[/bold]")
            console.print(f"Average Entropy: {results['average_entropy']:.2f}")
            
            # Sort by entropy descending
            sorted_files = sorted(results["files"], key=lambda x: x["entropy"], reverse=True)
            
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("File")
            table.add_column("Entropy")
            table.add_column("Size")
            table.add_column("Verdict")
            
            for file_info in sorted_files[:20]:  # Show top 20
                entropy = file_info["entropy"]
                verdict = "[green]Normal[/green]"
                if entropy > 7.5:
                    verdict = "[red]Packed/Encrypted[/red]"
                elif entropy > 6.0:
                    verdict = "[yellow]High[/yellow]"
                    
                table.add_row(
                    file_info["filename"],
                    f"{entropy:.2f}",
                    str(file_info["size"]),
                    verdict
                )
            console.print(table)
            if len(sorted_files) > 20:
                console.print(f"\n... and {len(sorted_files) - 20} more files.")
    
    elif args.analysis_type == "domains":
        from ..analysis.domains import analyze_domains
        from rich.table import Table
        
        results = analyze_domains(Path(args.file), show_progress=show_progress)
        
        if args.json:
            console.print_json(data=results)
        else:
            console.print(f"[bold]Domain Analysis for {args.file}[/bold]")
            
            console.print(f"\n[bold cyan]Unique Domains ({len(results['domains'])}):[/bold cyan]")
            if results["domains"]:
                for domain in results["domains"]:
                    console.print(f"  - {domain}")
            else:
                console.print("  [yellow]No domains found.[/yellow]")
                
            console.print(f"\n[bold cyan]URLs ({len(results['urls'])}):[/bold cyan]")
            if results["urls"]:
                # Show top 50 URLs to avoid spamming
                for url in results["urls"][:50]:
                    console.print(f"  - {url}")
                if len(results["urls"]) > 50:
                    console.print(f"  ... and {len(results['urls']) - 50} more.")
            else:
                console.print("  [yellow]No URLs found.[/yellow]")
    
    elif args.analysis_type == "secrets":
        from ..secrets import SecretScanner
        from rich.table import Table
        
        scanner = SecretScanner()
        results = scanner.scan_extension(Path(args.file))
        
        if args.json:
            # Convert dataclass to dict for JSON serialization
            import dataclasses
            console.print_json(data=[dataclasses.asdict(r) for r in results])
        else:
            console.print(f"[bold]Secret Scan for {args.file}[/bold]")
            
            if results:
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("Type")
                table.add_column("File")
                table.add_column("Line")
                table.add_column("Match (Masked)")
                
                for finding in results:
                    table.add_row(
                        finding.type,
                        finding.file,
                        str(finding.line),
                        finding.match
                    )
                console.print(table)
                console.print(f"\n[bold red]Found {len(results)} potential secrets.[/bold red]")
            else:
                console.print("\n[green]No secrets found.[/green]")

    elif args.analysis_type == "yara":
        from ..analysis.yara import YaraScanner
        from rich.table import Table
        
        try:
            scanner = YaraScanner(args.rules)
            results = scanner.scan_archive(Path(args.file))
            
            if args.json:
                console.print_json(data=results)
            else:
                console.print(f"[bold]YARA Scan for {args.file}[/bold]")
                console.print(f"Rules: {args.rules}")
                
                if results:
                    for filename, matches in results.items():
                        console.print(f"\n[bold cyan]File: {filename}[/bold cyan]")
                        table = Table(show_header=True, header_style="bold magenta")
                        table.add_column("Rule")
                        table.add_column("Tags")
                        table.add_column("Meta")
                        
                        for match in matches:
                            table.add_row(
                                match["rule"],
                                ", ".join(match["tags"]),
                                str(match["meta"])
                            )
                        console.print(table)
                else:
                    console.print("\n[green]No YARA matches found.[/green]")
                    
        except ImportError as e:
            console.print(f"[red]{e}[/red]")
            sys.exit(1)
        except Exception as e:
            console.print(f"[red]Error during YARA scan: {e}[/red]")
            sys.exit(1)
