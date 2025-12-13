# Plan: Extract Command

## Goal

Implement a standalone `extract` subcommand to unzip existing extension files (`.crx`, `.xpi`).

## Analysis

- **Current State**: Can only extract during download.
- **Requirement**: `fext extract <file>`.
- **Usage**: `fext extract my_extension.crx`.

## Strategy

1. **CLI Update**: Add `extract` (alias `x`) subcommand to `src/fetchext/cli.py`.
    - Argument: `file` (required).
    - Argument: `-o` / `--output-dir` (optional).
2. **Implementation**:
    - Reuse `open_extension_archive` from `src/fetchext/utils.py`.
    - If output dir is not specified, default to `current_dir / filename_stem`.
    - If output dir IS specified, extract directly there? Or extract to `output_dir / filename_stem`?
    - Standard behavior for `unzip` is to extract into current dir or specified dir.
    - Let's say:
        - `fext extract foo.crx` -> extracts to `./foo/` (to avoid cluttering).
        - `fext extract foo.crx -o dest` -> extracts to `dest/foo/` or `dest/`?
        - Let's follow the `download --extract` pattern: extract to a folder named after the extension.
        - So `fext extract foo.crx -o dest` -> `dest/foo/`.
        - Wait, if I want to extract *contents* to `dest`, I should be able to.
        - Let's stick to: always create a subdirectory based on filename stem, unless user explicitly says otherwise?
        - Simpler: `fext extract foo.crx` -> `./foo/`.
        - `fext extract foo.crx -o dest` -> `dest/`. (User is responsible for naming the folder if they want a specific one).
        - But `download --extract` does `output_dir / stem`.
        - Let's make `extract` command extract *into* the target directory.
        - If I run `fext extract foo.crx`, it should probably create `foo/` in CWD.
        - If I run `fext extract foo.crx -o bar/`, it should extract into `bar/`.
        - This gives maximum control.

## Files to Modify

- `src/fetchext/cli.py`: Add subcommand and logic.
- `tests/cli/test_cli.py`: Add test.

## Verification Plan

- Run `fext extract existing.crx`.
- Check output.
- Run `make test`.
