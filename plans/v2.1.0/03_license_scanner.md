# Plan: License Scanner

## Goal

Implement `fext scan --licenses <file>` to identify open source licenses in extension files.

## Problem

Auditors need to know the legal status of code within an extension (e.g., copy-pasted libraries).

## Solution

Scan for license files and headers.

## Implementation Details

### 1. CLI Command (`src/fetchext/commands/scan.py`)

- Add `--licenses` flag to `scan` command.

### 2. Core Logic (`src/fetchext/analysis/licenses.py`)

- Scan for filenames: `LICENSE`, `LICENSE.txt`, `COPYING`, `NOTICE`.
- Scan `package.json` for `"license"` field.
- Scan file headers (first 20 lines) for common license text (MIT, Apache, GPL, BSD).
- Use regex patterns for detection.

### 3. Output

- List detected licenses and the files they were found in.

## Verification

- Create dummy extension with `LICENSE` (MIT) and `script.js` (Apache header).
- Run `fext scan --licenses`.
- Verify output.
