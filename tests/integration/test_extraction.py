import zipfile
from pathlib import Path
from fetchext.cli import main
from unittest.mock import patch

def test_auto_extraction(fs, mocker):
    # Mock downloader
    mock_downloader_cls = mocker.patch("fetchext.cli.ChromeDownloader")
    mock_downloader = mock_downloader_cls.return_value
    mock_downloader.extract_id.return_value = "test_id"
    
    # Create a fake downloaded file (zip)
    output_dir = Path("/downloads")
    output_dir.mkdir()
    fake_crx = output_dir / "test_id.crx"
    
    # Create a valid zip file on the fake filesystem
    with zipfile.ZipFile(fake_crx, 'w') as zf:
        zf.writestr("manifest.json", '{"name": "Test"}')
        zf.writestr("script.js", "console.log('hello')")
        
    mock_downloader.download.return_value = fake_crx
    
    # Run CLI with --extract
    with patch("sys.argv", ["fext", "download", "chrome", "http://example.com", "-o", "/downloads", "--extract"]):
        main()
        
    # Check if extracted directory exists
    # The CLI uses output_path.stem as the directory name
    # output_path is /downloads/test_id.crx, stem is test_id
    extract_dir = output_dir / "test_id"
    assert extract_dir.exists()
    assert extract_dir.is_dir()
    assert (extract_dir / "manifest.json").exists()
    assert (extract_dir / "script.js").exists()
