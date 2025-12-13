# Plan: Parallel Grep

## Goal
Optimize the `fext grep` command to use parallel processing (`ProcessPoolExecutor`) for searching through large repositories of extensions. This will significantly reduce search time on multi-core systems.

## Objectives
1.  Refactor `src/fetchext/analysis/grep.py` (or wherever grep logic resides) to support parallel execution.
2.  Use `concurrent.futures.ProcessPoolExecutor` to distribute the workload (files or extensions) across available CPU cores.
3.  Ensure thread safety for result collection (or use `as_completed` to collect results in the main thread).
4.  Maintain the existing output format and functionality (regex support, case insensitivity).

## Implementation Details

### 1. Locate Grep Logic
- Currently likely in `src/fetchext/commands/audit.py` or `src/fetchext/core.py` or a dedicated module.
- I recall `tests/unit/test_grep.py`, so there might be a `src/fetchext/analysis/grep.py` or similar.

### 2. Refactoring
- Create a helper function `_grep_file(file_path, pattern, ignore_case)` that runs in a worker process.
- Update the main `grep` function to:
    - Collect all target files.
    - Submit tasks to the executor.
    - Collect and display results as they complete (streaming).

### 3. Performance
- Benchmark before and after using the new `benchmarks/` suite (add a grep benchmark).

## Verification
- Run `tests/unit/test_grep.py` to ensure no regression.
- Run `benchmarks/run.py` (after adding grep benchmark) to verify speedup.
