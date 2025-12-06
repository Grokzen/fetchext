import json
import pytest
from unittest.mock import patch
from fetchext.history import HistoryManager

@pytest.fixture
def mock_history_file(tmp_path):
    return tmp_path / "history.json"

@pytest.fixture
def history_manager(mock_history_file):
    with patch("fetchext.history.HistoryManager._get_history_path", return_value=mock_history_file):
        yield HistoryManager()

def test_add_entry(history_manager, mock_history_file):
    history_manager.add_entry("download", "abc", "chrome", "1.0", "success", "/tmp/file.crx")
    
    assert mock_history_file.exists()
    with open(mock_history_file, "r") as f:
        data = json.load(f)
        assert len(data) == 1
        assert data[0]["id"] == "abc"
        assert data[0]["action"] == "download"
        assert data[0]["status"] == "success"

def test_get_entries(history_manager):
    history_manager.add_entry("download", "1", "chrome")
    history_manager.add_entry("download", "2", "chrome")
    
    entries = history_manager.get_entries()
    assert len(entries) == 2
    # Should be sorted by timestamp desc (newest first)
    assert entries[0]["id"] == "2"
    assert entries[1]["id"] == "1"

def test_get_entries_limit(history_manager):
    for i in range(5):
        history_manager.add_entry("download", str(i), "chrome")
        
    entries = history_manager.get_entries(limit=3)
    assert len(entries) == 3
    assert entries[0]["id"] == "4"

def test_clear(history_manager, mock_history_file):
    history_manager.add_entry("download", "abc", "chrome")
    assert mock_history_file.exists()
    
    history_manager.clear()
    assert not mock_history_file.exists()

def test_corrupt_file(history_manager, mock_history_file):
    mock_history_file.write_text("{invalid json")
    
    # Should handle gracefully and return empty list
    entries = history_manager.get_entries()
    assert entries == []
    
    # Should overwrite corrupt file on add
    history_manager.add_entry("download", "abc", "chrome")
    entries = history_manager.get_entries()
    assert len(entries) == 1
