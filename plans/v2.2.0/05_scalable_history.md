# Plan: Scalable History

## Goal

Migrate `history` tracking to an optional SQLite backend to support repositories with thousands of extensions.

## Details

- Current implementation uses `history.json`.
- New implementation should use `history.db` (SQLite).
- Automatic migration from JSON to SQLite on first run.
- Backward compatibility (keep `HistoryManager` API).

## Implementation Steps

1. Modify `src/fetchext/history.py`.
    - Create `SqliteBackend` class.
    - Update `HistoryManager` to initialize SQLite connection.
    - Implement `migrate_json_to_sqlite` method.
2. Schema:

    ```sql
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        extension_id TEXT,
        browser TEXT,
        version TEXT,
        action TEXT,
        status TEXT,
        path TEXT,
        timestamp TEXT
    );
    CREATE INDEX idx_ext_id ON history(extension_id);
    ```

3. Update tests.

## Dependencies

- `sqlite3` (standard lib).
