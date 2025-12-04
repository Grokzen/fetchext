import pytest
import requests
from pathlib import Path
from fetchext.downloaders.chrome import ChromeDownloader

class TestDownloadFlow:
    def test_chrome_download_success(self, fs, mocker):
        # Mock requests.get
        mock_response = mocker.Mock()
        mock_response.iter_content = lambda chunk_size: [b"fake_content"]
        mock_response.headers = {"content-disposition": 'attachment; filename="extension.crx"'}
        mock_response.raise_for_status = mocker.Mock()
        
        mocker.patch("requests.get", return_value=mock_response)

        downloader = ChromeDownloader()
        extension_id = "abcdefghijklmnop"
        output_dir = Path("/tmp/test_download")
        fs.create_dir(output_dir)
        
        output_path = downloader.download(extension_id, output_dir)

        assert output_path.exists()
        assert output_path.read_bytes() == b"fake_content"
        assert output_path.name == "extension.crx"

    def test_chrome_download_404(self, fs, mocker):
        # Mock requests.get to raise HTTPError
        mocker.patch("requests.get", side_effect=requests.HTTPError("404 Not Found"))

        downloader = ChromeDownloader()
        extension_id = "invalid_id"
        output_dir = Path("/tmp/test_download")
        fs.create_dir(output_dir)

        with pytest.raises(requests.HTTPError):
            downloader.download(extension_id, output_dir)

    def test_chrome_download_empty_file_cleanup(self, fs, mocker):
        # Mock requests.get to return empty content
        mock_response = mocker.Mock()
        mock_response.iter_content = lambda chunk_size: [] # Empty content
        mock_response.headers = {}
        mock_response.raise_for_status = mocker.Mock()

        mocker.patch("requests.get", return_value=mock_response)

        downloader = ChromeDownloader()
        extension_id = "empty_extension"
        output_dir = Path("/tmp/test_download")
        fs.create_dir(output_dir)

        with pytest.raises(RuntimeError, match="Download failed: File is empty"):
            downloader.download(extension_id, output_dir)
        
        # Verify file was cleaned up
        assert not (output_dir / "empty_extension.crx").exists()
