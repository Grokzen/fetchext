# Plan: Snapshot Testing

## Goal

Implement snapshot testing to detect unintended visual changes in CLI output and TUI screens.

## Objectives

1. Add `pytest-snapshot` (or `syrupy`) dependency.
2. Create a new test suite `tests/snapshot/`.
3. Implement tests that capture CLI output (stdout/stderr) and compare against stored snapshots.
4. Implement tests that capture TUI screens (using `textual`'s SVG export or string representation) and compare against snapshots.

## Implementation Details

### 1. Dependencies

Add `syrupy` to `requirements-dev.txt` (it's generally better/more modern than `pytest-snapshot`).

### 2. CLI Snapshots

* Use `capsys` fixture to capture output.
* Use `snapshot` fixture from `syrupy` to verify.
* Test commands: `fext --help`, `fext info`, `fext report --json`.

### 3. TUI Snapshots

* Textual has built-in snapshot testing capabilities via `App.run_test()`.
* We can verify the screen content.

## Risks

* Snapshots can be brittle if output contains timestamps or dynamic paths.
* We need to ensure deterministic output (mocking time, paths).

## Verification

* Run tests and generate initial snapshots.
* Modify code to change output and verify tests fail.
