# Plan: Performance Benchmarks

## Goal

Establish a benchmarking suite to measure and track the performance of critical `fetchext` operations (extraction, analysis, parsing) over time. This will help detect performance regressions and guide optimization efforts.

## Objectives

1. Create a `benchmarks/` directory.
2. Implement benchmarks using `pytest-benchmark` (if available) or a custom script using `timeit` / `time`.
    * Since `pytest-benchmark` is not in `requirements-dev.txt`, we will use a custom Python script `benchmarks/run.py` that uses `timeit` and reports results.
3. Benchmark Scenarios:
    * **CRX Parsing**: Speed of `CrxDecoder.get_id` and `get_zip_offset`.
    * **Extraction**: Speed of extracting a medium-sized extension (mocked or real sample).
    * **Analysis**: Speed of `complexity`, `entropy`, and `secrets` analysis on a sample set.
4. Output: JSON report and console table.

## Implementation Details

### 1. Directory Structure

```text
benchmarks/
  __init__.py
  run.py
  samples/ (optional, or generate on fly)
```

### 2. `benchmarks/run.py`

* Use `timeit` to run functions multiple times.
* Use `rich.table` to display results.
* Generate synthetic extension data (large JS files, many small files) to test different characteristics.

### 3. Scenarios

* `bench_crx_parse`: Parse a 10MB CRX header.
* `bench_entropy`: Calculate entropy of 100 files (10KB each).
* `bench_complexity`: Calculate complexity of a large JS file (5000 lines).
* `bench_secrets`: Scan a large file for secrets.

## Verification

* Run `python3 benchmarks/run.py` and verify it produces output.
