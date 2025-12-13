# Plan: History Concurrency (WAL Mode)

## Goal

Enable Write-Ahead Logging (WAL) mode for the SQLite history database to improve concurrency and reliability when multiple `fext` instances are running.

## Motivation

Currently, the SQLite database uses the default rollback journal mode. This can lead to `database is locked` errors if multiple processes try to write to the history (e.g., parallel batch downloads or running multiple terminal sessions). WAL mode allows simultaneous readers and writers, significantly reducing contention.

## Implementation Details

### 1. Update `HistoryManager`

- File: `src/fetchext/history.py` (or wherever `HistoryManager` is defined, likely `src/fetchext/history_sqlite.py` based on previous context).
- Method: `__init__` or `_init_db`.
- Action: Execute `PRAGMA journal_mode=WAL;` immediately after connection.
- Action: Set a busy timeout (e.g., 5000ms) to wait for locks instead of failing immediately.

### 2. Verification

- Create a test that simulates concurrent writes.
- Verify that `PRAGMA journal_mode` returns `wal`.

## Testing Strategy

- **Unit Test**: Mock the sqlite connection and verify the PRAGMA calls.
- **Integration Test**: Spawn multiple threads/processes writing to the same DB file and ensure no data is lost and no locking errors occur.

## Documentation

- Update `docs/configuration.md` (if relevant, though this is an internal fix).
- Update `CHANGELOG.md`.
