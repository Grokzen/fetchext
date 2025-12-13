import pytest
from fetchext.mirror import MirrorManager

@pytest.fixture
def mock_downloader(mocker):
    # Mock ChromeDownloader
    mock = mocker.patch("fetchext.mirror.ChromeDownloader")
    instance = mock.return_value
    instance.extract_id.side_effect = lambda url: url if len(url) == 32 else "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    instance.get_latest_version.return_value = "2.0"
    return instance

@pytest.fixture
def mock_inspector(mocker):
    return mocker.patch("fetchext.mirror.ExtensionInspector")

def test_sync_download_missing(tmp_path, mock_downloader):
    # Setup
    list_file = tmp_path / "list.txt"
    list_file.write_text("chrome aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    output_dir = tmp_path / "extensions"
    
    manager = MirrorManager()
    manager.sync(list_file, output_dir, show_progress=False)
    
    # Verify download called
    mock_downloader.download.assert_called_with("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", output_dir, show_progress=False)

def test_sync_update_available(tmp_path, mock_downloader, mock_inspector):
    # Setup
    list_file = tmp_path / "list.txt"
    list_file.write_text("chrome aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    output_dir = tmp_path / "extensions"
    output_dir.mkdir()
    (output_dir / "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.crx").touch()
    
    # Mock local version
    inspector_instance = mock_inspector.return_value
    inspector_instance.get_manifest.return_value = {"version": "1.0"}
    
    # Mock remote version (already 2.0 in fixture)
    
    manager = MirrorManager()
    manager.sync(list_file, output_dir, show_progress=False)
    
    # Verify download called (update)
    mock_downloader.download.assert_called_with("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", output_dir, show_progress=False)

def test_sync_up_to_date(tmp_path, mock_downloader, mock_inspector):
    # Setup
    list_file = tmp_path / "list.txt"
    list_file.write_text("chrome aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    output_dir = tmp_path / "extensions"
    output_dir.mkdir()
    (output_dir / "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.crx").touch()
    
    # Mock local version
    inspector_instance = mock_inspector.return_value
    inspector_instance.get_manifest.return_value = {"version": "2.0"}
    
    manager = MirrorManager()
    manager.sync(list_file, output_dir, show_progress=False)
    
    # Verify download NOT called
    mock_downloader.download.assert_not_called()

def test_prune(tmp_path, mock_downloader):
    # Setup
    list_file = tmp_path / "list.txt"
    list_file.write_text("chrome aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    output_dir = tmp_path / "extensions"
    output_dir.mkdir()
    
    # Valid file
    (output_dir / "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.crx").touch()
    # Invalid file
    (output_dir / "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb.crx").touch()
    
    # Mock download to avoid actual download logic if file missing (it's there)
    mock_downloader.get_latest_version.return_value = None # Skip update check
    
    manager = MirrorManager()
    manager.sync(list_file, output_dir, prune=True, show_progress=False)
    
    assert (output_dir / "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.crx").exists()
    assert not (output_dir / "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb.crx").exists()
