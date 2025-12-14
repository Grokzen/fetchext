import base64
import difflib
import mimetypes
from pathlib import Path
from fetchext.workflow.diff  import DiffReport
from fetchext.utils  import open_extension_archive

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Visual Diff Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; color: #333; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ border-bottom: 2px solid #eee; padding-bottom: 10px; }}
        h2 {{ margin-top: 30px; color: #444; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; background: #f8f9fa; padding: 20px; border-radius: 6px; }}
        .stat-box {{ text-align: center; }}
        .stat-value {{ font-size: 24px; font-weight: bold; color: #0366d6; }}
        .stat-label {{ color: #666; font-size: 14px; }}
        
        .file-diff {{ margin-bottom: 40px; border: 1px solid #e1e4e8; border-radius: 6px; overflow: hidden; }}
        .file-header {{ background: #f6f8fa; padding: 10px 15px; border-bottom: 1px solid #e1e4e8; font-family: monospace; font-weight: bold; }}
        
        .diff-content {{ padding: 15px; overflow-x: auto; }}
        
        /* Image Diff Styles */
        .image-comparison {{ display: flex; justify-content: space-around; align-items: flex-start; gap: 20px; }}
        .image-box {{ text-align: center; flex: 1; }}
        .image-box img {{ max-width: 100%; max-height: 400px; border: 1px solid #ddd; background: #fff; background-image: linear-gradient(45deg, #eee 25%, transparent 25%, transparent 75%, #eee 75%, #eee), linear-gradient(45deg, #eee 25%, transparent 25%, transparent 75%, #eee 75%, #eee); background-size: 20px 20px; background-position: 0 0, 10px 10px; }}
        .image-label {{ margin-top: 10px; font-weight: bold; color: #555; }}
        .image-meta {{ font-size: 12px; color: #777; margin-top: 5px; }}

        /* Text Diff Styles */
        table.diff {{ width: 100%; font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace; font-size: 12px; border-collapse: collapse; }}
        table.diff td {{ padding: 2px 5px; white-space: pre-wrap; word-break: break-all; }}
        .diff_header {{ background-color: #e1e4e8; color: #24292e; text-align: right; width: 1%; min-width: 30px; user-select: none; }}
        .diff_next {{ background-color: #e1e4e8; }}
        .diff_add {{ background-color: #ccffd8; }}
        .diff_chg {{ background-color: #fff5b1; }}
        .diff_sub {{ background-color: #ffdce0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Visual Diff Report</h1>
        
        <div class="summary">
            <div class="stat-box">
                <div class="stat-value">{old_version}</div>
                <div class="stat-label">Old Version</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{new_version}</div>
                <div class="stat-label">New Version</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{added_count}</div>
                <div class="stat-label">Added Files</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{removed_count}</div>
                <div class="stat-label">Removed Files</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{modified_count}</div>
                <div class="stat-label">Modified Files</div>
            </div>
        </div>

        <h2>Modified Files</h2>
        {content}
    </div>
</body>
</html>
"""


class VisualDiffGenerator:
    def generate(
        self, report: DiffReport, old_path: Path, new_path: Path, output_path: Path
    ):
        content_parts = []

        with (
            open_extension_archive(old_path) as old_zf,
            open_extension_archive(new_path) as new_zf,
        ):
            for filename in report.modified_files:
                try:
                    old_bytes = old_zf.read(filename)
                    new_bytes = new_zf.read(filename)

                    if self._is_image(filename):
                        diff_html = self._generate_image_diff(
                            filename, old_bytes, new_bytes
                        )
                    elif self._is_text(filename):
                        diff_html = self._generate_text_diff(
                            filename, old_bytes, new_bytes
                        )
                    else:
                        diff_html = f"<div class='diff-content'><p>Binary file modified (size: {len(old_bytes)} -> {len(new_bytes)} bytes)</p></div>"

                    content_parts.append(f"""
                    <div class="file-diff">
                        <div class="file-header">{filename}</div>
                        {diff_html}
                    </div>
                    """)
                except Exception as e:
                    content_parts.append(f"""
                    <div class="file-diff">
                        <div class="file-header">{filename}</div>
                        <div class="diff-content">Error generating diff: {str(e)}</div>
                    </div>
                    """)

        html = HTML_TEMPLATE.format(
            old_version=report.old_version,
            new_version=report.new_version,
            added_count=len(report.added_files),
            removed_count=len(report.removed_files),
            modified_count=len(report.modified_files),
            content="\n".join(content_parts),
        )

        output_path.write_text(html, encoding="utf-8")

    def _is_image(self, filename: str) -> bool:
        mime, _ = mimetypes.guess_type(filename)
        return mime and mime.startswith("image/")

    def _is_text(self, filename: str) -> bool:
        mime, _ = mimetypes.guess_type(filename)
        if mime and (
            mime.startswith("text/")
            or mime in ["application/json", "application/javascript", "application/xml"]
        ):
            return True
        # Fallback for common extensions
        return filename.lower().endswith(
            (
                ".js",
                ".css",
                ".html",
                ".json",
                ".txt",
                ".md",
                ".xml",
                ".ts",
                ".jsx",
                ".tsx",
            )
        )

    def _generate_image_diff(
        self, filename: str, old_bytes: bytes, new_bytes: bytes
    ) -> str:
        old_b64 = base64.b64encode(old_bytes).decode("ascii")
        new_b64 = base64.b64encode(new_bytes).decode("ascii")
        mime, _ = mimetypes.guess_type(filename)
        mime = mime or "image/png"

        return f"""
        <div class="diff-content">
            <div class="image-comparison">
                <div class="image-box">
                    <div class="image-label">Old</div>
                    <img src="data:{mime};base64,{old_b64}" alt="Old Image">
                    <div class="image-meta">{len(old_bytes)} bytes</div>
                </div>
                <div class="image-box">
                    <div class="image-label">New</div>
                    <img src="data:{mime};base64,{new_b64}" alt="New Image">
                    <div class="image-meta">{len(new_bytes)} bytes</div>
                </div>
            </div>
        </div>
        """

    def _generate_text_diff(
        self, filename: str, old_bytes: bytes, new_bytes: bytes
    ) -> str:
        try:
            old_text = old_bytes.decode("utf-8", errors="replace").splitlines()
            new_text = new_bytes.decode("utf-8", errors="replace").splitlines()

            diff = difflib.HtmlDiff(wrapcolumn=80).make_table(
                old_text,
                new_text,
                fromdesc="Old",
                todesc="New",
                context=True,
                numlines=5,
            )
            return f"<div class='diff-content'>{diff}</div>"
        except Exception as e:
            return f"<div class='diff-content'>Error decoding text: {str(e)}</div>"
