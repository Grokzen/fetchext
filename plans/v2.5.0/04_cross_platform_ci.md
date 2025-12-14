# Plan: Cross-Platform CI

## Goal

Expand GitHub Actions workflow to include Windows and macOS runners to ensure cross-platform compatibility.

## Objectives

1. Modify `.github/workflows/ci.yml`.
2. Update the `test` job to run on a matrix of operating systems: `ubuntu-latest`, `windows-latest`, `macos-latest`.
3. Ensure tests pass on all platforms (this might reveal path handling bugs).
4. Handle platform-specific issues (e.g., file permissions, path separators).

## Implementation Details

### 1. Workflow Update

* Change `runs-on: ubuntu-latest` to `runs-on: ${{ matrix.os }}`.
* Add `matrix` strategy with `os: [ubuntu-latest, windows-latest, macos-latest]`.
* Keep Python version matrix as well.

### 2. Test Adjustments

* Some tests might fail on Windows due to path separators or file locking.
* `pyfakefs` usually handles this well, but real file operations in integration tests might be tricky.
* We might need to skip certain tests on Windows if they rely on Unix-specific features (like permissions).

## Risks

* Windows tests might be slow.
* Path handling bugs might be exposed (which is the point).

## Verification

* Since I cannot run GitHub Actions locally, I will rely on the fact that I've updated the workflow file.
* I can try to simulate some checks if possible, but mostly this is a configuration change.
