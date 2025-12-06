from unittest.mock import MagicMock
from pathlib import Path
from fetchext import core
from fetchext.history import HistoryManager

def test_download_updates_history(fs, mocker):
    # Mock downloader
    mock_downloader = MagicMock()
    mock_downloader.extract_id.return_value = "abc"
    mock_downloader.download.return_value = Path("/tmp/out/ext.crx")
    
    mocker.patch("fetchext.core.get_downloader", return_value=mock_downloader)
    
    # Mock HistoryManager to verify calls, but also let it write to fs if we wanted
    # But here we just want to verify it's called or the file is created.
    # Since we are using pyfakefs, we can check the file.
    
    # We need to patch _get_history_path to point to a known location in fake fs
    history_path = Path("/tmp/history.json")
    mocker.patch("fetchext.history.HistoryManager._get_history_path", return_value=history_path)
    
    output_dir = Path("/tmp/out")
    fs.create_dir(output_dir)
    
    core.download_extension("chrome", "http://example.com", output_dir)
    
    assert history_path.exists()
    manager = HistoryManager()
    entries = manager.get_entries()
    assert len(entries) == 1
    assert entries[0]["id"] == "abc"
    assert entries[0]["action"] == "download"

def test_extract_updates_history(fs, mocker):
    # Create a fake extension file
    ext_path = Path("/tmp/ext.crx")
    fs.create_file(ext_path, contents=b"fake zip content")
    
    # Mock open_extension_archive to avoid real zip parsing
    mock_zf = MagicMock()
    mocker.patch("fetchext.core.open_extension_archive", return_value=mock_zf)
    mock_zf.__enter__.return_value = mock_zf
    mock_zf.__exit__.return_value = None
    
    # Patch history path
    history_path = Path("/tmp/history.json")
    mocker.patch("fetchext.history.HistoryManager._get_history_path", return_value=history_path)
    
    core.extract_extension(ext_path)
    
    assert history_path.exists()
    manager = HistoryManager()
    entries = manager.get_entries()
    assert len(entries) == 1
    assert entries[0]["action"] == "extract"
    # ID and browser will be unknown because no metadata sidecar
    assert entries[0]["id"] == "unknown"
