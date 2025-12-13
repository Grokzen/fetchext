from pathlib import Path
from ..console import console
from ..reporter import BadgeGenerator
from ..inspector import ExtensionInspector
from ..risk import RiskAnalyzer
from ..analysis.licenses import scan_licenses

def register(subparsers):
    badge_parser = subparsers.add_parser("badge", help="Generate SVG badges for extension")
    badge_parser.add_argument("file", type=Path, help="Path to extension file")
    badge_parser.add_argument(
        "-o", "--output-dir",
        type=Path,
        default=Path("."),
        help="Output directory for badges"
    )
    badge_parser.set_defaults(func=handle_badge)

def handle_badge(args, show_progress=True):
    file_path = args.file
    if not file_path.exists():
        console.print(f"[red]File not found: {file_path}[/red]")
        return

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    
    base_name = file_path.stem

    # 1. Version Badge
    try:
        inspector = ExtensionInspector()
        manifest = inspector.get_manifest(file_path)
        version = manifest.get("version", "unknown")
        
        svg = BadgeGenerator.generate("version", version, "blue")
        out = output_dir / f"{base_name}_version.svg"
        out.write_text(svg, encoding="utf-8")
        console.print(f"Generated [bold]{out}[/bold]")
    except Exception as e:
        console.print(f"[yellow]Failed to generate version badge: {e}[/yellow]")

    # 2. Risk Badge
    try:
        analyzer = RiskAnalyzer()
        report = analyzer.analyze(file_path)
        
        color_map = {
            "Critical": "red",
            "High": "orange",
            "Medium": "yellow",
            "Low": "blue",
            "Safe": "brightgreen"
        }
        color = color_map.get(report.max_level, "grey")
        
        svg = BadgeGenerator.generate("risk", report.max_level, color)
        out = output_dir / f"{base_name}_risk.svg"
        out.write_text(svg, encoding="utf-8")
        console.print(f"Generated [bold]{out}[/bold]")
    except Exception as e:
        console.print(f"[yellow]Failed to generate risk badge: {e}[/yellow]")

    # 3. License Badge
    try:
        licenses = scan_licenses(file_path)
        if licenses:
            # Pick the first one or join them
            lic_name = list(licenses.keys())[0]
            if len(licenses) > 1:
                lic_name += "+"
            
            svg = BadgeGenerator.generate("license", lic_name, "green")
            out = output_dir / f"{base_name}_license.svg"
            out.write_text(svg, encoding="utf-8")
            console.print(f"Generated [bold]{out}[/bold]")
        else:
            svg = BadgeGenerator.generate("license", "unknown", "grey")
            out = output_dir / f"{base_name}_license.svg"
            out.write_text(svg, encoding="utf-8")
            console.print(f"Generated [bold]{out}[/bold]")
    except Exception as e:
        console.print(f"[yellow]Failed to generate license badge: {e}[/yellow]")
