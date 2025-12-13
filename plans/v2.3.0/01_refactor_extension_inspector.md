# Plan: Refactor ExtensionInspector for Robustness

## Goal

Make `ExtensionInspector` resilient to malformed manifests and corrupt archives, ensuring that analysis tools (like `report`, `scan`) can continue processing even if individual extensions are problematic.

## Current State

- `ExtensionInspector.get_manifest(path)` raises `ValueError` if:
  - Archive is invalid.
  - `manifest.json` is missing.
  - `manifest.json` is invalid JSON.
- `ExtensionInspector.get_timeline(path)` raises `ValueError` on archive errors.
- Callers (e.g., `reporter.py`, `core.py`) often wrap these in try/except, but a unified "safe" inspection method is missing.

## Proposed Changes

### 1. Enhance `ExtensionInspector`

- Add a new method `inspect(file_path) -> InspectionResult`.
- `InspectionResult` will be a dataclass or dict containing:
  - `manifest`: Dict or None
  - `timeline`: List or None
  - `errors`: List of error strings
  - `valid`: Boolean (True if critical parts like manifest are present)
- Implement `inspect` to try extracting each component independently.
  - If manifest fails, record error but continue to timeline.
  - If archive is totally corrupt, record fatal error.

### 2. Update `get_manifest`

- Keep it for backward compatibility, but maybe improve the error message.
- Or delegate to `inspect` and raise if `manifest` is None.

### 3. Refactor Consumers

- Update `src/fetchext/reporter.py` to use `inspect` and report errors in the generated report instead of crashing or skipping the file entirely.
- Update `src/fetchext/commands/visualize.py` if applicable.

## Implementation Steps

1. Define `InspectionResult` structure.
2. Implement `ExtensionInspector.inspect(file_path)`.
3. Add unit tests for `inspect` with:
    - Valid extension.
    - Extension with invalid JSON manifest.
    - Extension missing manifest.
    - Corrupt ZIP file.
4. Verify that `get_manifest` still works as expected (or refactor it to use `inspect`).

## Verification

- Run `pytest tests/unit/test_inspector.py`.
- Create a test case with a "broken" CRX and ensure `inspect` returns partial data (e.g., timeline might work even if manifest is bad, though usually manifest is first).
- Actually, if ZIP is valid, we can list files (timeline) even if `manifest.json` is garbage.
