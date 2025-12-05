# Plan: Auto-Extraction

## Goal

Implement an `--extract` / `-x` flag for the `download` command that automatically unzips the downloaded extension into a directory.

## Analysis

- **Current State**: Downloads file only.
- **Requirement**: Unzip to a folder named after the extension.
- **Challenge**: CRX files might have headers that standard `zipfile` doesn't like. `ExtensionInspector` already handles this.

## Strategy

1. **Refactoring**: Extract the "safe zip opening" logic from `ExtensionInspector` into a reusable utility function `open_extension_archive` in `src/fetchext/utils.py`.
2. **CLI Update**: Add `--extract` argument to `download` command.
3. **Implementation**:
    - In `cli.py`, if `--extract` is set:
        - Determine extract directory (e.g., `output_dir / filename_stem`).
        - Use `open_extension_archive` to get the ZipFile object.
        - `zf.extractall(extract_dir)`.
        - Log success.

## Files to Modify

- `src/fetchext/utils.py`: Create new file.
- `src/fetchext/inspector.py`: Refactor to use `utils.py`.
- `src/fetchext/cli.py`: Add flag and logic.
- `tests/integration/test_extraction.py`: Add tests.

## Verification Plan

- Run `fext download ... --extract`.
- Check if directory exists and contains files.
- Run `make test`.
