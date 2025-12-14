import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

from .inspector import ExtensionInspector
from .risk import RiskAnalyzer
from .exceptions import ExtensionError

class MarkdownReporter:
    """Generates Markdown reports for extension files."""

    def __init__(self, file_path: Path):
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise ExtensionError(f"File not found: {self.file_path}")
        
        self.inspector = ExtensionInspector()
        self.risk_analyzer = RiskAnalyzer()

    def _calculate_hash(self, algorithm: str = "sha256") -> str:
        """Calculate file hash."""
        hash_func = getattr(hashlib, algorithm)()
        with self.file_path.open("rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        return hash_func.hexdigest()

    def _format_size(self, size_bytes: int) -> str:
        """Format file size."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"

    def generate(self) -> str:
        """Generate the Markdown report content."""
        inspection = self.inspector.inspect(self.file_path)
        manifest = inspection["manifest"] or {}
        
        # If inspection failed completely, we might want to note that
        errors = inspection.get("errors", [])
        
        risk_report = self.risk_analyzer.analyze(self.file_path)
        
        # File Info
        file_stat = self.file_path.stat()
        file_size = self._format_size(file_stat.st_size)
        sha256_hash = self._calculate_hash("sha256")
        md5_hash = self._calculate_hash("md5")
        
        # Manifest Info
        name = manifest.get("name", "Unknown")
        version = manifest.get("version", "Unknown")
        description = manifest.get("description", "No description provided.")
        author = manifest.get("author", "Unknown")
        homepage = manifest.get("homepage_url", "N/A")
        update_url = manifest.get("update_url", "N/A")
        manifest_version = manifest.get("manifest_version", 2)
        
        # File Tree
        file_count = 0
        file_tree_summary = "Could not read file structure."
        
        if inspection["timeline"]:
            file_list = [item["filename"] for item in inspection["timeline"]]
            file_count = len(file_list)
            file_tree_summary = self._generate_tree_text(file_list)
        elif errors:
             file_tree_summary = f"Error reading archive: {'; '.join(errors)}"

        # Risk Color
        risk_emoji = {
            "Critical": "🔴",
            "High": "🟠",
            "Medium": "🟡",
            "Low": "🔵",
            "Safe": "🟢"
        }.get(risk_report.max_level, "⚪")

        report = []
        
        # Header
        report.append(f"# Extension Report: {name}")
        report.append(f"**Generated on:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
        
        # Summary Table
        report.append("## 📦 Metadata")
        report.append("| Field | Value |")
        report.append("|---|---|")
        report.append(f"| **Name** | {name} |")
        report.append(f"| **Version** | {version} |")
        report.append(f"| **Manifest Version** | V{manifest_version} |")
        report.append(f"| **Author** | {author} |")
        report.append(f"| **Size** | {file_size} |")
        report.append(f"| **File** | `{self.file_path.name}` |")
        report.append(f"| **SHA256** | `{sha256_hash}` |")
        report.append(f"| **MD5** | `{md5_hash}` |")
        report.append(f"| **Homepage** | {homepage} |")
        report.append(f"| **Update URL** | {update_url} |")
        report.append("")
        
        report.append("## 📝 Description")
        report.append(f"> {description}\n")
        
        # Risk Analysis
        report.append("## 🛡️ Risk Analysis")
        report.append(f"**Overall Risk Level:** {risk_emoji} **{risk_report.max_level}** (Score: {risk_report.total_score})\n")
        
        if risk_report.risky_permissions:
            report.append("### ⚠️ Risky Permissions")
            report.append("| Permission | Level | Score | Description |")
            report.append("|---|---|---|---|")
            for p in risk_report.risky_permissions:
                report.append(f"| `{p.permission}` | {p.level} | {p.score} | {p.description} |")
            report.append("")
            
        if risk_report.safe_permissions:
            report.append("### ✅ Safe / Other Permissions")
            report.append(", ".join(f"`{p}`" for p in risk_report.safe_permissions))
            report.append("")

        # File Structure
        report.append(f"## 📂 File Structure ({file_count} files)")
        report.append("```text")
        report.append(file_tree_summary)
        report.append("```\n")
        
        # Full Manifest
        report.append("## 📜 Full Manifest")
        report.append("<details>")
        report.append("<summary>Click to expand manifest.json</summary>")
        report.append("")
        report.append("```json")
        report.append(json.dumps(manifest, indent=2))
        report.append("```")
        report.append("</details>")
        
        return "\n".join(report)

    def _generate_tree_text(self, file_list: list[str]) -> str:
        """Generate a simple text tree for markdown."""
        # Simplified tree generation
        # Just show top level and count children
        tree = {}
        for path in file_list:
            parts = path.split("/")
            current = tree
            for part in parts:
                if part not in current:
                    current[part] = {}
                current = current[part]
        
        lines = []
        self._print_tree(tree, lines)
        
        # Truncate if too long
        if len(lines) > 50:
            return "\n".join(lines[:50]) + f"\n... ({len(lines) - 50} more lines)"
        return "\n".join(lines)

    def _print_tree(self, node: dict, lines: list, prefix: str = ""):
        keys = sorted(node.keys())
        for i, key in enumerate(keys):
            is_last = (i == len(keys) - 1)
            connector = "└── " if is_last else "├── "
            lines.append(f"{prefix}{connector}{key}")
            
            if node[key]: # Is directory
                extension = "    " if is_last else "│   "
                self._print_tree(node[key], lines, prefix + extension)

    def save(self, output_path: Path):
        """Save the report to a file."""
        content = self.generate()
        with output_path.open("w", encoding="utf-8") as f:
            f.write(content)


class HtmlReporter:
    """Generates HTML reports for extension files."""

    def __init__(self, report_data: dict):
        self.data = report_data

    def generate(self) -> str:
        """Generate the HTML report content."""
        meta = self.data.get("metadata", {})
        manifest = meta.get("manifest", {})
        risk = self.data.get("risk_analysis", {})
        
        name = manifest.get("name", "Unknown")
        version = manifest.get("version", "Unknown")
        manifest_version = manifest.get("manifest_version", 2)
        size = self._format_size(meta.get("size", 0))
        date = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        
        risk_level = risk.get("max_level", "Unknown")
        risk_score = risk.get("total_score", 0)
        risk_class = f"risk-{risk_level.lower()}"

        # Complexity Data
        complexity = self.data.get("complexity", {})
        avg_complexity = complexity.get("average_complexity", 0)
        max_complexity = complexity.get("max_complexity", 0)
        total_functions = complexity.get("total_functions", 0)
        high_complexity_funcs = complexity.get("high_complexity_functions", [])

        # Prepare Complexity Table
        complexity_rows = ""
        for func in high_complexity_funcs[:20]:  # Limit to top 20
            complexity_rows += f"""
            <tr>
                <td>{func['file']}</td>
                <td><code>{func['function']}</code></td>
                <td>{func['complexity']}</td>
                <td>{func['length']}</td>
            </tr>
            """
        
        complexity_table = f"""
        <table>
            <thead>
                <tr>
                    <th>File</th>
                    <th>Function</th>
                    <th>Complexity</th>
                    <th>Length</th>
                </tr>
            </thead>
            <tbody>
                {complexity_rows if complexity_rows else '<tr><td colspan="4">No high complexity functions found.</td></tr>'}
            </tbody>
        </table>
        """

        # Prepare Risk Table
        risk_rows = ""
        for p in risk.get("risky_permissions", []):
            level_class = f"risk-{p['level'].lower()}"
            risk_rows += f"""
            <tr>
                <td><code>{p['permission']}</code></td>
                <td class="{level_class}">{p['level']}</td>
                <td>{p['score']}</td>
                <td>{p['description']}</td>
            </tr>
            """
        
        risk_table = f"""
        <table>
            <thead>
                <tr>
                    <th>Permission</th>
                    <th>Level</th>
                    <th>Score</th>
                    <th>Description</th>
                </tr>
            </thead>
            <tbody>
                {risk_rows if risk_rows else '<tr><td colspan="4">No risky permissions found.</td></tr>'}
            </tbody>
        </table>
        """

        # Prepare Secrets Table
        secrets = self.data.get("secrets", [])
        secret_rows = ""
        for s in secrets:
            secret_rows += f"""
            <tr>
                <td>{s['type']}</td>
                <td>{s['file']}</td>
                <td>{s['line']}</td>
                <td><code>{s['match']}</code></td>
            </tr>
            """
        
        secrets_table = f"""
        <table>
            <thead>
                <tr>
                    <th>Type</th>
                    <th>File</th>
                    <th>Line</th>
                    <th>Match</th>
                </tr>
            </thead>
            <tbody>
                {secret_rows if secret_rows else '<tr><td colspan="4">No secrets found.</td></tr>'}
            </tbody>
        </table>
        """

        # Prepare Domains
        domains = self.data.get("domains", [])
        domains_list = "<ul>" + "".join(f"<li><a href='http://{d}' target='_blank'>{d}</a></li>" for d in domains[:50]) + "</ul>"
        if len(domains) > 50:
            domains_list += f"<p>... and {len(domains) - 50} more.</p>"
        if not domains:
            domains_list = "<p>No domains found.</p>"

        # Chart Data
        risk_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Safe": 0}
        for p in risk.get("risky_permissions", []):
            if p['level'] in risk_counts:
                risk_counts[p['level']] += 1
        
        # File Types (Entropy data usually has file list)
        entropy_data = self.data.get("entropy", {}).get("files", [])
        file_exts = {}
        for f in entropy_data:
            ext = Path(f['filename']).suffix or "no-ext"
            file_exts[ext] = file_exts.get(ext, 0) + 1
        
        # Sort and limit file exts
        sorted_exts = dict(sorted(file_exts.items(), key=lambda item: item[1], reverse=True)[:10])

        # Complexity Chart Data
        top_complex = sorted(high_complexity_funcs, key=lambda x: x['complexity'], reverse=True)[:10]
        complex_labels = [f"{f['function']} ({Path(f['file']).name})" for f in top_complex]
        complex_data = [f['complexity'] for f in top_complex]

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Extension Report: {name}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
        .container {{ background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1, h2, h3 {{ color: #2c3e50; margin-top: 30px; }}
        .header {{ border-bottom: 1px solid #eee; padding-bottom: 20px; margin-bottom: 30px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .card {{ background: #fff; border: 1px solid #e1e4e8; border-radius: 6px; padding: 20px; }}
        .stat {{ font-size: 24px; font-weight: bold; color: #0366d6; }}
        .label {{ color: #586069; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 14px; }}
        th, td {{ text-align: left; padding: 12px; border-bottom: 1px solid #eee; }}
        th {{ background-color: #f8f9fa; font-weight: 600; }}
        .risk-critical {{ color: #d73a49; font-weight: bold; }}
        .risk-high {{ color: #cb2431; font-weight: bold; }}
        .risk-medium {{ color: #b08800; }}
        .risk-low {{ color: #0366d6; }}
        .risk-safe {{ color: #28a745; }}
        pre {{ background: #f6f8fa; padding: 15px; border-radius: 6px; overflow-x: auto; }}
        .chart-container {{ position: relative; height: 250px; width: 100%; }}
        code {{ background: #f0f0f0; padding: 2px 4px; border-radius: 3px; font-family: monospace; }}
        ul {{ list-style-type: none; padding: 0; }}
        li {{ margin-bottom: 5px; }}
        a {{ color: #0366d6; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Extension Report: {name}</h1>
            <p>Generated on {date}</p>
        </div>
        
        <div class="grid">
            <div class="card">
                <div class="label">Version</div>
                <div class="stat">{version}</div>
            </div>
            <div class="card">
                <div class="label">Risk Score</div>
                <div class="stat {risk_class}">{risk_score} ({risk_level})</div>
            </div>
            <div class="card">
                <div class="label">Manifest</div>
                <div class="stat">V{manifest_version}</div>
            </div>
            <div class="card">
                <div class="label">Size</div>
                <div class="stat">{size}</div>
            </div>
        </div>

        <div class="grid">
            <div class="card">
                <div class="label">Avg Complexity</div>
                <div class="stat">{avg_complexity:.2f}</div>
            </div>
            <div class="card">
                <div class="label">Max Complexity</div>
                <div class="stat">{max_complexity}</div>
            </div>
            <div class="card">
                <div class="label">Total Functions</div>
                <div class="stat">{total_functions}</div>
            </div>
        </div>

        <div class="grid">
            <div class="card">
                <h3>Risk Distribution</h3>
                <div class="chart-container">
                    <canvas id="riskChart"></canvas>
                </div>
            </div>
            <div class="card">
                <h3>File Types</h3>
                <div class="chart-container">
                    <canvas id="fileChart"></canvas>
                </div>
            </div>
            <div class="card">
                <h3>Top Complex Functions</h3>
                <div class="chart-container">
                    <canvas id="complexityChart"></canvas>
                </div>
            </div>
        </div>

        <h2>🛡️ Risk Analysis</h2>
        {risk_table}

        <h2>🧠 Complexity Analysis</h2>
        {complexity_table}

        <h2>🔐 Secrets Found</h2>
        {secrets_table}

        <h2>🌐 Domains & URLs</h2>
        {domains_list}

        <h2>📜 Manifest</h2>
        <details>
            <summary>Click to expand</summary>
            <pre>{json.dumps(manifest, indent=2)}</pre>
        </details>
    </div>
    <script>
        const riskCtx = document.getElementById('riskChart').getContext('2d');
        new Chart(riskCtx, {{
            type: 'doughnut',
            data: {{
                labels: {json.dumps(list(risk_counts.keys()))},
                datasets: [{{
                    data: {json.dumps(list(risk_counts.values()))},
                    backgroundColor: ['#d73a49', '#cb2431', '#b08800', '#0366d6', '#28a745']
                }}]
            }},
            options: {{ maintainAspectRatio: false }}
        }});

        const fileCtx = document.getElementById('fileChart').getContext('2d');
        new Chart(fileCtx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(list(sorted_exts.keys()))},
                datasets: [{{
                    label: 'File Count',
                    data: {json.dumps(list(sorted_exts.values()))},
                    backgroundColor: '#0366d6'
                }}]
            }},
            options: {{ maintainAspectRatio: false }}
        }});

        const complexityCtx = document.getElementById('complexityChart').getContext('2d');
        new Chart(complexityCtx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(complex_labels)},
                datasets: [{{
                    label: 'Cyclomatic Complexity',
                    data: {json.dumps(complex_data)},
                    backgroundColor: '#d73a49'
                }}]
            }},
            options: {{ maintainAspectRatio: false, indexAxis: 'y' }}
        }});
    </script>
</body>
</html>"""
        return html

    def _format_size(self, size_bytes: int) -> str:
        """Format file size."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"

    def save(self, output_path: Path):
        """Save the report to a file."""
        content = self.generate()
        with output_path.open("w", encoding="utf-8") as f:
            f.write(content)


class BadgeGenerator:
    """Generates SVG badges."""
    
    COLORS = {
        "green": "#4c1",
        "blue": "#007ec6",
        "red": "#e05d44",
        "yellow": "#dfb317",
        "orange": "#fe7d37",
        "grey": "#555",
        "brightgreen": "#4c1"
    }

    @staticmethod
    def generate(label: str, message: str, color: str = "blue") -> str:
        """Generate an SVG badge."""
        color_hex = BadgeGenerator.COLORS.get(color, color)
        
        # Approximate text width (very rough estimation)
        # 6px per char + 10px padding
        label_width = len(label) * 7 + 10
        msg_width = len(message) * 7 + 10
        total_width = label_width + msg_width
        
        return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="20">
    <linearGradient id="b" x2="0" y2="100%">
        <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
        <stop offset="1" stop-opacity=".1"/>
    </linearGradient>
    <mask id="a">
        <rect width="{total_width}" height="20" rx="3" fill="#fff"/>
    </mask>
    <g mask="url(#a)">
        <path fill="#555" d="M0 0h{label_width}v20H0z"/>
        <path fill="{color_hex}" d="M{label_width} 0h{msg_width}v20H{label_width}z"/>
        <path fill="url(#b)" d="M0 0h{total_width}v20H0z"/>
    </g>
    <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
        <text x="{label_width/2}" y="15" fill="#010101" fill-opacity=".3">{label}</text>
        <text x="{label_width/2}" y="14">{label}</text>
        <text x="{label_width + msg_width/2}" y="15" fill="#010101" fill-opacity=".3">{message}</text>
        <text x="{label_width + msg_width/2}" y="14">{message}</text>
    </g>
</svg>"""


