import sqlite3
import threading
import time
from fetchext.data.history import HistoryManager


def test_wal_mode_enabled(tmp_path, monkeypatch):
    # Mock base dir to use tmp_path
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))

    manager = HistoryManager()

    # Check if WAL mode is enabled
    with sqlite3.connect(manager.db_path) as conn:
        cursor = conn.execute("PRAGMA journal_mode;")
        mode = cursor.fetchone()[0]
        assert mode.upper() == "WAL"


def test_concurrent_writes(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    manager = HistoryManager()

    def write_entries(thread_id):
        # Create a new manager instance per thread to simulate processes/connections
        local_manager = HistoryManager()
        for i in range(50):
            local_manager.add_entry(
                action="download",
                extension_id=f"ext_{thread_id}_{i}",
                browser="chrome",
                version="1.0",
            )
            time.sleep(0.001)  # Slight delay to increase overlap chance

    threads = []
    for i in range(4):
        t = threading.Thread(target=write_entries, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # Verify all entries are present
    entries = manager.get_all_entries()
    assert len(entries) == 200
