import pytest
import json
from unittest.mock import patch
from fetchext.data.history import HistoryManager


@pytest.fixture
def mock_base_dir(tmp_path):
    with patch("fetchext.data.history.HistoryManager._get_base_dir", return_value=tmp_path):
        yield tmp_path


def test_history_init(mock_base_dir):
    HistoryManager()
    assert (mock_base_dir / "history.db").exists()


def test_history_add_get(mock_base_dir):
    manager = HistoryManager()
    manager.add_entry("download", "abc", "chrome", "1.0")

    entries = manager.get_entries()
    assert len(entries) == 1
    assert entries[0]["id"] == "abc"
    assert entries[0]["action"] == "download"


def test_history_migration(mock_base_dir):
    # Create legacy JSON
    json_path = mock_base_dir / "history.json"
    json_path.write_text(
        json.dumps(
            [
                {
                    "timestamp": "2023-01-01",
                    "action": "old",
                    "id": "old_id",
                    "browser": "firefox",
                }
            ]
        )
    )

    manager = HistoryManager()

    # Check migration
    entries = manager.get_entries()
    assert len(entries) == 1
    assert entries[0]["id"] == "old_id"

    # Check backup
    assert (mock_base_dir / "history.json.bak").exists()
    assert not json_path.exists()


def test_history_clear(mock_base_dir):
    manager = HistoryManager()
    manager.add_entry("test", "1", "c")
    manager.clear()
    assert len(manager.get_entries()) == 0
