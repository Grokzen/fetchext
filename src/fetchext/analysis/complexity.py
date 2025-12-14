import zipfile
import concurrent.futures
import os
from pathlib import Path
from typing import Dict, Any, List
from ..crx import CrxDecoder
from ..console import console


def _analyze_file_content(name: str, content: str) -> List[Dict[str, Any]]:
    """Helper function to run in a separate process."""
    import lizard

    results = []
    analysis = lizard.analyze_file.analyze_source_code(name, content)
    for func in analysis.function_list:
        results.append(
            {
                "file": name,
                "function": func.name,
                "complexity": func.cyclomatic_complexity,
                "length": func.length,
                "params": func.parameter_count,
            }
        )
    return results


def analyze_complexity(file_path: Path, show_progress: bool = True) -> Dict[str, Any]:
    """
    Analyzes the cyclomatic complexity of JavaScript files in an extension.
    Uses parallel processing for performance.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Determine if it's a CRX and get offset
    offset = 0
    try:
        offset = CrxDecoder.get_zip_offset(file_path)
    except Exception:
        # Not a CRX or error parsing, assume ZIP/XPI (offset 0)
        pass

    results = []

    with open(file_path, "rb") as f:
        f.seek(offset)
        try:
            with zipfile.ZipFile(f) as zf:
                # Collect JS files
                js_files = [name for name in zf.namelist() if name.endswith(".js")]

                max_workers = os.cpu_count() or 4
                with concurrent.futures.ProcessPoolExecutor(
                    max_workers=max_workers
                ) as executor:
                    futures = []
                    for name in js_files:
                        with zf.open(name) as js_file:
                            content = js_file.read().decode("utf-8", errors="ignore")
                            futures.append(
                                executor.submit(_analyze_file_content, name, content)
                            )

                    if show_progress:
                        with console.create_progress() as progress:
                            task = progress.add_task(
                                "Analyzing Complexity", total=len(futures)
                            )
                            for future in concurrent.futures.as_completed(futures):
                                try:
                                    file_results = future.result()
                                    results.extend(file_results)
                                except Exception:
                                    pass  # Ignore errors in individual files
                                finally:
                                    progress.advance(task)
                    else:
                        for future in concurrent.futures.as_completed(futures):
                            try:
                                file_results = future.result()
                                results.extend(file_results)
                            except Exception:
                                pass  # Ignore errors in individual files

        except zipfile.BadZipFile:
            raise ValueError("Invalid zip/crx file")

    # Aggregate stats
    if not results:
        return {
            "average_complexity": 0,
            "max_complexity": 0,
            "high_complexity_functions": [],
            "total_functions": 0,
        }

    total_complexity = sum(r["complexity"] for r in results)
    max_complexity = max(r["complexity"] for r in results)
    avg_complexity = total_complexity / len(results)

    # Filter high complexity (> 15 is usually considered complex)
    high_complexity = [r for r in results if r["complexity"] > 15]
    high_complexity.sort(key=lambda x: x["complexity"], reverse=True)

    return {
        "average_complexity": avg_complexity,
        "max_complexity": max_complexity,
        "high_complexity_functions": high_complexity,
        "total_functions": len(results),
    }
