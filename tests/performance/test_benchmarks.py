import time
import shutil
from fetchext.utils import open_extension_archive
from fetchext.analysis.complexity import analyze_complexity
from fetchext.analysis.entropy import analyze_entropy


def test_crx_parsing_speed(large_extension_crx):
    """
    Benchmark CRX parsing (finding zip offset and opening).
    Target: < 0.1s for 10MB file.
    """
    start = time.perf_counter()

    with open_extension_archive(large_extension_crx) as zf:
        assert len(zf.namelist()) == 100

    duration = time.perf_counter() - start
    print(f"\nCRX Parsing Duration: {duration:.4f}s")

    # CI environments can be slow, so we set a generous upper bound
    # but locally this should be very fast.
    assert duration < 0.5, f"CRX parsing took too long: {duration:.4f}s"


def test_extraction_speed(large_extension_crx, tmp_path):
    """
    Benchmark extraction speed.
    Target: < 1.0s for 10MB (100 files).
    """
    output_dir = tmp_path / "extracted"

    start = time.perf_counter()

    with open_extension_archive(large_extension_crx) as zf:
        zf.extractall(output_dir)

    duration = time.perf_counter() - start
    print(f"\nExtraction Duration: {duration:.4f}s")

    assert duration < 2.0, f"Extraction took too long: {duration:.4f}s"
    assert len(list(output_dir.glob("*"))) == 100


def test_analysis_complexity_speed(large_extension_dir, tmp_path):
    """
    Benchmark complexity analysis speed.
    Target: < 2.0s for 100 files.
    """
    # Zip the directory first
    zip_path = tmp_path / "large_ext.zip"
    shutil.make_archive(str(zip_path.with_suffix("")), "zip", large_extension_dir)

    start = time.perf_counter()

    results = analyze_complexity(zip_path)

    duration = time.perf_counter() - start
    print(f"\nComplexity Analysis Duration: {duration:.4f}s")

    assert duration < 5.0, f"Complexity analysis took too long: {duration:.4f}s"
    assert len(results["high_complexity_functions"]) == 0  # Our dummy code is simple
    assert results["total_functions"] == 10000  # 100 functions per file * 100 files


def test_analysis_entropy_speed(large_extension_dir, tmp_path):
    """
    Benchmark entropy analysis speed.
    Target: < 1.0s for 100 files.
    """
    # Zip the directory first
    zip_path = tmp_path / "large_ext.zip"
    shutil.make_archive(str(zip_path.with_suffix("")), "zip", large_extension_dir)

    start = time.perf_counter()

    results = analyze_entropy(zip_path)

    duration = time.perf_counter() - start
    print(f"\nEntropy Analysis Duration: {duration:.4f}s")

    assert duration < 3.0, f"Entropy analysis took too long: {duration:.4f}s"
    assert len(results["files"]) == 100
