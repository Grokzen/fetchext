import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

from .inspector import ExtensionInspector
from .risk import RiskAnalyzer
from .utils import open_extension_archive

class MarkdownReporter:
    """Generates Markdown reports for extension files."""

    def __init__(self, file_path: Path):
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")
        
        self.inspector = ExtensionInspector()
        self.risk_analyzer = RiskAnalyzer()

    def _calculate_hash(self, algorithm: str = "sha256") -> str:
        """Calculate file hash."""
        hash_func = getattr(hashlib, algorithm)()
        with open(self.file_path, "rb") as f:
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
        manifest = self.inspector.get_manifest(self.file_path)
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
        try:
            with open_extension_archive(self.file_path) as zf:
                file_list = zf.namelist()
            # Use the existing build_file_tree but capture its output (it returns a Tree object from rich)
            # Since rich Tree objects aren't easily convertible to Markdown, we might need a simplified version
            # or just list top-level files/dirs.
            # Actually, let's just list the top 20 files or structure.
            # For a report, a full tree might be too long. Let's do a summary.
            file_count = len(file_list)
            file_tree_summary = self._generate_tree_text(file_list)
        except Exception:
            file_tree_summary = "Could not read file structure."
            file_count = 0

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
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
