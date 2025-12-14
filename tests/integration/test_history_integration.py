from unittest.mock import MagicMock
from pathlib import Path
from fetchext import core


def test_download_updates_history(fs, mocker):
    # Mock downloader
    mock_downloader = MagicMock()
    mock_downloader.extract_id.return_value = "abc"
    mock_downloader.download.return_value = Path("/tmp/out/ext.crx")

    mocker.patch("fetchext.core.get_downloader", return_value=mock_downloader)

    # Mock HistoryManager to verify calls, but also let it write to fs if we wanted
    # But here we just want to verify it's called or the file is created.
    # Since we are using pyfakefs, we can check the file.

    # Mock HistoryManager to avoid sqlite3 issues with pyfakefs
    mock_history_manager = MagicMock()
    mocker.patch("fetchext.core.HistoryManager", return_value=mock_history_manager)

    output_dir = Path("/tmp/out")
    fs.create_dir(output_dir)

    core.download_extension("chrome", "http://example.com", output_dir)

    # Verify add_entry was called
    mock_history_manager.add_entry.assert_called_once()
    call_args = mock_history_manager.add_entry.call_args
    assert call_args.kwargs.get("action") == "download"
    assert call_args.kwargs.get("extension_id") == "abc"


def test_extract_updates_history(fs, mocker):
    # Create a fake extension file
    ext_path = Path("/tmp/ext.crx")
    fs.create_file(ext_path, contents=b"fake zip content")

    # Mock open_extension_archive to avoid real zip parsing
    mock_zf = MagicMock()
    mocker.patch("fetchext.core.open_extension_archive", return_value=mock_zf)
    mock_zf.__enter__.return_value = mock_zf
    mock_zf.__exit__.return_value = None

    # Mock HistoryManager
    mock_history_manager = MagicMock()
    mocker.patch("fetchext.core.HistoryManager", return_value=mock_history_manager)

    core.extract_extension(ext_path)

    # Verify add_entry was called
    mock_history_manager.add_entry.assert_called_once()
    call_args = mock_history_manager.add_entry.call_args
    assert call_args.kwargs.get("action") == "extract"
