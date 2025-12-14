# Plan: SQL Query Interface

## Goal

Add `fext query <sql>` command to execute raw SQL queries against `history.db`.

## Steps

1. **Update `HistoryManager`**:
    * Add `execute_query(self, sql: str) -> List[Dict[str, Any]]` method to `src/fetchext/history.py`.
    * Ensure it returns a list of dictionaries (using `sqlite3.Row`).
    * Handle `sqlite3.Error` and re-raise as `ExtensionError`.
2. **Create `src/fetchext/commands/query.py`**:
    * Implement `register(subparsers)` to add the `query` subcommand.
    * Implement `handle_query(args)`:
        * Call `HistoryManager().execute_query(args.sql)`.
        * If `--json`, print JSON.
        * If `--csv`, print CSV.
        * Default: Print a `rich.table.Table` with dynamic columns.
3. **Register Command**:
    * Update `src/fetchext/cli.py` to import `fetchext.commands.query` and call `query.register(subparsers)`.
4. **Testing**:
    * Add `tests/unit/test_history_query.py` to verify SQL execution.
    * Add `tests/cli/test_query.py` to verify CLI output formats.

## Security Considerations

* This is a power user feature.
* It allows arbitrary SQL execution against the local SQLite DB.
* Since it's a local CLI tool operating on the user's own data, SQL injection is less of a concern (the user *is* the injector), but we should document it as such.
* We might want to restrict to read-only queries (SELECT) if possible, but SQLite doesn't easily enforce this on a connection level without extensions. We can check if the query starts with SELECT, but that's easily bypassed. For a developer tool, full access is acceptable.
