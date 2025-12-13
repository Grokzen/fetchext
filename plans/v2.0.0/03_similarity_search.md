# Plan: Similarity Search

## Goal

Implement `fext similar <file>` to find other extensions in the local repository with high code similarity using fuzzy hashing.

## Problem

Malicious extensions often copy code from legitimate ones or other malicious extensions, changing only minor details. Exact matching fails here.

## Solution

Use Context Triggered Piecewise Hashing (CTPH), specifically `ssdeep` (via `ppdeep` for pure Python support), to generate fuzzy hashes of extension source code and compare them.

## Implementation Details

### 1. Dependencies

- Add `ppdeep` to `pyproject.toml`.

### 2. Core Logic (`src/fetchext/analysis/similarity.py`)

- `SimilarityEngine` class.
- Method `compute_hash(path)`:
  - If path is a file (CRX/ZIP): Read content of all JS files inside, concatenate, and hash.
  - If path is a directory: Walk, read JS files, concatenate, hash.
- Method `find_similar(target_path, repository_path)`:
  - Compute hash of target.
  - Iterate over all extensions in repository.
  - Compute hash for each (cache this later?).
  - Compare using `ppdeep.compare(h1, h2)`.
  - Return list of matches with score > threshold.

### 3. CLI (`src/fetchext/commands/similar.py`)

- Command: `fext similar <path>`
- Options:
  - `--threshold` / `-t`: Minimum similarity score (0-100, default 50).
  - `--json`: JSON output.

### 4. Testing

- Unit tests with slightly modified strings to verify fuzzy matching.

## Verification

- Create two dummy extensions with slightly different JS.
- Run `fext similar ext1.crx` and ensure it finds `ext2.crx`.
