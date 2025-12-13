# Plan: Update All

## Goal

Implement `fext update --all` to check and update all extensions currently tracked in the local repository/history.

## Problem

Users have many extensions downloaded. Updating them one by one is tedious.

## Solution

Iterate through the download history, check for updates, and download new versions if available.

## Implementation Details

### 1. CLI Command (`src/fetchext/commands/update.py`)

- `fext update --all`
- Reuse `fext check` logic but perform the download.

### 2. Core Logic

- Load history from `src/fetchext/history.py`.
- Get unique Extension IDs and their last known versions.
- For each extension:
  - Query Web Store for latest version.
  - Compare with local version.
  - If newer, download using `download_extension`.

### 3. Concurrency

- Use `ThreadPoolExecutor` to check/update in parallel.

## Verification

- Mock history with 2 outdated extensions.
- Run `fext update --all`.
- Verify new versions are downloaded.
