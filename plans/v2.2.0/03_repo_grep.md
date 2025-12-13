# Plan: Repo Grep

## Goal

Implement `fext grep <pattern>` to search for string patterns across the source code of *all* downloaded extensions.

## Details

- Search in the configured download directory.
- Support both extracted directories and compressed archives (CRX/XPI/ZIP).
- Use regex or simple string matching.
- Output: `File:Line: Match context`.
- Parallel execution for performance.

## Implementation Steps

1. Create `src/fetchext/commands/grep.py`.
2. Register command in `cli.py`.
3. Implement `GrepSearcher` in `src/fetchext/analysis/grep.py`.
    - Method `search(directory, pattern, recursive=True)`.
    - Handle archives transparently using `zipfile` / `CrxDecoder`.
4. Implement `handle_grep` in `grep.py`.

## Dependencies

- `concurrent.futures` (standard lib).
