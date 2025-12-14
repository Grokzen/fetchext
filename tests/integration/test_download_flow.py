import pytest
import requests
from pathlib import Path
from fetchext.downloaders.chrome import ChromeDownloader


class TestDownloadFlow:
    def test_chrome_download_success(self, fs, mocker):
        # Mock NetworkClient
        mock_client = mocker.Mock()
        mock_client.download_file.return_value = Path(
            "/tmp/test_download/abcdefghijklmnop.crx"
        )

        # Create the file that download_file would create
        fs.create_file(
            "/tmp/test_download/abcdefghijklmnop.crx", contents="fake_content"
        )

        mocker.patch(
            "fetchext.downloaders.base.NetworkClient", return_value=mock_client
        )

        downloader = ChromeDownloader()
        extension_id = "abcdefghijklmnop"
        output_dir = Path("/tmp/test_download")
        # fs.create_dir(output_dir) # Already created by create_file

        output_path = downloader.download(extension_id, output_dir)

        assert output_path.exists()
        assert output_path.read_bytes() == b"fake_content"
        mock_client.download_file.assert_called_once()

    def test_chrome_download_404(self, fs, mocker):
        from fetchext.core.exceptions import NetworkError

        mock_client = mocker.Mock()
        mock_client.download_file.side_effect = requests.HTTPError("404 Not Found")

        mocker.patch(
            "fetchext.downloaders.base.NetworkClient", return_value=mock_client
        )

        downloader = ChromeDownloader()
        extension_id = "invalid_id"
        output_dir = Path("/tmp/test_download")
        fs.create_dir(output_dir)

        with pytest.raises(NetworkError):
            downloader.download(extension_id, output_dir)

    def test_chrome_download_empty_file_cleanup(self, fs, mocker):
        from fetchext.core.exceptions import NetworkError

        mock_client = mocker.Mock()
        mock_client.download_file.side_effect = NetworkError(
            "Download failed: File is empty"
        )

        mocker.patch(
            "fetchext.downloaders.base.NetworkClient", return_value=mock_client
        )

        downloader = ChromeDownloader()
        extension_id = "empty_extension"
        output_dir = Path("/tmp/test_download")
        fs.create_dir(output_dir)

        with pytest.raises(NetworkError, match="Download failed: File is empty"):
            downloader.download(extension_id, output_dir)
