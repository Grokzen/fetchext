import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class HistoryManager:
    def __init__(self):
        self.base_dir = self._get_base_dir()
        self.db_path = self.base_dir / "history.db"
        self.json_path = self.base_dir / "history.json"
        self._init_db()
        self._migrate_json()

    def _get_base_dir(self) -> Path:
        xdg_data_home = os.environ.get("XDG_DATA_HOME")
        if xdg_data_home:
            base_dir = Path(xdg_data_home)
        else:
            base_dir = Path.home() / ".local" / "share"
        return base_dir / "fext"

    def _get_connection(self) -> sqlite3.Connection:
        """Get a configured SQLite connection with WAL mode enabled."""
        conn = sqlite3.connect(self.db_path, timeout=5.0)
        # Enable Write-Ahead Logging for better concurrency
        conn.execute("PRAGMA journal_mode=WAL;")
        # Enable foreign keys (good practice, though not strictly used yet)
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    def _init_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    action TEXT,
                    extension_id TEXT,
                    browser TEXT,
                    version TEXT,
                    status TEXT,
                    path TEXT
                )
            """)
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_timestamp ON history(timestamp DESC)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_ext_id ON history(extension_id)"
            )

    def _migrate_json(self):
        if self.json_path.exists():
            try:
                with open(self.json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                if data:
                    with self._get_connection() as conn:
                        # Check if DB is empty to avoid double migration
                        cursor = conn.execute("SELECT count(*) FROM history")
                        if cursor.fetchone()[0] == 0:
                            for entry in data:
                                conn.execute(
                                    """
                                    INSERT INTO history (timestamp, action, extension_id, browser, version, status, path)
                                    VALUES (?, ?, ?, ?, ?, ?, ?)
                                """,
                                    (
                                        entry.get("timestamp"),
                                        entry.get("action"),
                                        entry.get("id"),
                                        entry.get("browser"),
                                        entry.get("version"),
                                        entry.get("status"),
                                        entry.get("path"),
                                    ),
                                )

                # Rename JSON file to indicate migration done
                self.json_path.rename(self.json_path.with_suffix(".json.bak"))
            except Exception:
                pass

    def add_entry(
        self,
        action: str,
        extension_id: str,
        browser: str,
        version: Optional[str] = None,
        status: str = "success",
        path: Optional[str] = None,
    ) -> None:
        timestamp = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO history (timestamp, action, extension_id, browser, version, status, path)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    timestamp,
                    action,
                    extension_id,
                    browser,
                    version,
                    status,
                    str(path) if path else None,
                ),
            )

    def get_entries(self, limit: int = 20) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT timestamp, action, extension_id as id, browser, version, status, path
                FROM history
                ORDER BY timestamp DESC
                LIMIT ?
            """,
                (limit,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_all_entries(self) -> List[Dict[str, Any]]:
        """Get all entries for bulk operations."""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT timestamp, action, extension_id as id, browser, version, status, path
                FROM history
                ORDER BY timestamp DESC
            """)
            return [dict(row) for row in cursor.fetchall()]

    def execute_query(self, sql: str) -> List[Dict[str, Any]]:
        """Execute a raw SQL query."""
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(sql)
                # If it's a SELECT (or returns rows), fetch results
                if cursor.description:
                    return [dict(row) for row in cursor.fetchall()]
                return []
        except sqlite3.Error as e:
            raise e

    def clear(self) -> None:
        with self._get_connection() as conn:
            conn.execute("DELETE FROM history")
