import re
import zipfile
from pathlib import Path
from typing import Dict, Any
from collections import Counter
from ..crx import CrxDecoder


def analyze_api_usage(file_path: Path, show_progress: bool = False) -> Dict[str, Any]:
    """
    Analyzes the usage of Chrome/Browser APIs in the extension.
    Handles both directories and archives (CRX, XPI, ZIP).
    """
    api_pattern = re.compile(
        r"\b(chrome|browser)\.([a-zA-Z0-9_]+)(?:\.([a-zA-Z0-9_]+))?"
    )

    api_counts = Counter()
    file_api_map = {}

    if file_path.is_dir():
        return _analyze_directory(file_path, api_pattern)

    # Handle Archive
    offset = 0
    try:
        offset = CrxDecoder.get_zip_offset(file_path)
    except Exception:
        pass

    try:
        with open(file_path, "rb") as f:
            f.seek(offset)
            with zipfile.ZipFile(f) as zf:
                # Scan JS and HTML files
                target_files = [
                    name
                    for name in zf.namelist()
                    if name.endswith((".js", ".html", ".htm"))
                ]

                for name in target_files:
                    try:
                        with zf.open(name) as zf_file:
                            content = zf_file.read().decode("utf-8", errors="ignore")
                            _scan_content(
                                name, content, api_pattern, api_counts, file_api_map
                            )
                    except Exception:
                        continue
    except Exception as e:
        return {"error": str(e)}

    return _format_results(api_counts, file_api_map)


def _analyze_directory(directory: Path, pattern: re.Pattern) -> Dict[str, Any]:
    api_counts = Counter()
    file_api_map = {}

    files = (
        list(directory.rglob("*.js"))
        + list(directory.rglob("*.html"))
        + list(directory.rglob("*.htm"))
    )

    for file_path in files:
        try:
            content = file_path.read_text(errors="ignore")
            rel_path = str(file_path.relative_to(directory))
            _scan_content(rel_path, content, pattern, api_counts, file_api_map)
        except Exception:
            continue

    return _format_results(api_counts, file_api_map)


def _scan_content(
    filename: str,
    content: str,
    pattern: re.Pattern,
    global_counts: Counter,
    file_map: Dict,
):
    matches = pattern.findall(content)

    if matches:
        file_apis = []
        for match in matches:
            # match is (namespace, api, method) e.g. ('chrome', 'tabs', 'create')
            namespace, api, method = match
            full_api = f"{namespace}.{api}"
            if method:
                full_api += f".{method}"

            global_counts[full_api] += 1
            file_apis.append(full_api)

        if file_apis:
            file_map[filename] = dict(Counter(file_apis).most_common())


def _format_results(api_counts: Counter, file_map: Dict) -> Dict[str, Any]:
    return {
        "total_calls": sum(api_counts.values()),
        "unique_apis": len(api_counts),
        "api_counts": dict(api_counts.most_common()),
        "file_map": file_map,
    }
