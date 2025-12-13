# Plan: Code Beautifier

## Goal
Implement `fext beautify <file>` to format minified JavaScript and JSON files for better readability.

## Problem
Extensions often contain minified or obfuscated code, making it difficult to analyze logic or review for security issues.

## Solution
Add a command that uses `jsbeautifier` to format JavaScript and JSON files.

## Implementation Details

### 1. Dependencies
- Add `jsbeautifier` to `pyproject.toml`.

### 2. Core Logic (`src/fetchext/beautify.py`)
- Create `Beautifier` class.
- Support formatting of:
  - Single file (JS/JSON).
  - Directory (recursive).
  - In-place modification or output to stdout/new file.

### 3. CLI (`src/fetchext/commands/beautify.py`)
- Command: `fext beautify <path> [options]`
- Options:
  - `--in-place` / `-i`: Modify file in place.
  - `--output` / `-o`: Output file path.

### 4. Testing
- Unit tests for JS and JSON formatting.
- Integration tests for CLI.

## Verification
- Run `fext beautify test.min.js` and check output.
