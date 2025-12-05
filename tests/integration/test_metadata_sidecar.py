import json
from pathlib import Path
from fetchext.cli import main
from unittest.mock import patch

def test_metadata_sidecar_creation(fs, mocker):
    # Mock downloader
    mock_downloader_cls = mocker.patch("fetchext.core.ChromeDownloader")
    mock_downloader = mock_downloader_cls.return_value
    mock_downloader.extract_id.return_value = "test_id"
    
    # Create a fake downloaded file
    output_dir = Path("/downloads")
    output_dir.mkdir()
    fake_crx = output_dir / "test_id.crx"
    fs.create_file(fake_crx)
    
    mock_downloader.download.return_value = fake_crx
    
    # Mock ExtensionInspector
    mock_inspector_cls = mocker.patch("fetchext.core.ExtensionInspector")
    mock_inspector = mock_inspector_cls.return_value
    mock_inspector.get_manifest.return_value = {
        "name": "Test Extension",
        "version": "1.0.0"
    }
    
    # Run CLI
    with patch("sys.argv", ["fext", "download", "chrome", "http://example.com", "-o", "/downloads", "--save-metadata"]):
        main()
        
    # Check if metadata file exists
    metadata_path = output_dir / "test_id.crx.json"
    assert metadata_path.exists()
    
    with open(metadata_path, "r") as f:
        data = json.load(f)
        
    assert data["id"] == "test_id"
    assert data["name"] == "Test Extension"
    assert data["version"] == "1.0.0"
    assert data["source_url"] == "http://example.com"
    assert "download_timestamp" in data
    assert data["filename"] == "test_id.crx"
