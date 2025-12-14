import pytest
import zipfile
import concurrent.futures
from unittest.mock import patch
from pathlib import Path
from fetchext.analysis.complexity import analyze_complexity


def test_analyze_complexity_zip(fs):
    # Create a zip file with JS
    # Note: pyfakefs handles zipfile creation if fs is active

    # We need to write real bytes for zipfile to work with pyfakefs correctly
    # or use the real filesystem if pyfakefs has issues with zipfile (it usually works)

    js_simple = "function foo() { return 1; }"
    js_complex = """
    function bar(x) { 
        if(x) { 
            if(x) { 
                if(x) { 
                    return 1; 
                } 
            } 
        } 
        return 0; 
    }
    """

    # Create the zip file in the fake filesystem
    zip_path = Path("/test.zip")
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("simple.js", js_simple)
        zf.writestr("complex.js", js_complex)
        zf.writestr("manifest.json", "{}")  # Non-JS file

    with patch(
        "fetchext.analysis.complexity.concurrent.futures.ProcessPoolExecutor",
        concurrent.futures.ThreadPoolExecutor,
    ):
        results = analyze_complexity(zip_path)

    assert results["total_functions"] == 2
    # foo: 1, bar: 4. Avg: 2.5
    assert results["average_complexity"] == 2.5
    assert results["max_complexity"] == 4


def test_analyze_complexity_empty(fs):
    zip_path = Path("/empty.zip")
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("manifest.json", "{}")

    with patch(
        "fetchext.analysis.complexity.concurrent.futures.ProcessPoolExecutor",
        concurrent.futures.ThreadPoolExecutor,
    ):
        results = analyze_complexity(zip_path)
    assert results["total_functions"] == 0
    assert results["average_complexity"] == 0


def test_analyze_complexity_not_found(fs):
    with pytest.raises(FileNotFoundError):
        analyze_complexity(Path("/nonexistent.zip"))
