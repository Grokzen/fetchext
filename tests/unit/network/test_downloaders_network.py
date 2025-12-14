import pytest
from unittest.mock import MagicMock, patch
from fetchext.downloaders.chrome import ChromeDownloader
from fetchext.downloaders.edge import EdgeDownloader
from fetchext.downloaders.firefox import FirefoxDownloader


@pytest.fixture
def mock_client():
    with patch("fetchext.downloaders.base.NetworkClient") as MockClient:
        client_instance = MockClient.return_value
        yield client_instance


class TestChromeDownloaderNetwork:
    def test_get_latest_version(self, mock_client):
        downloader = ChromeDownloader()
        # Ensure the downloader uses the mocked client
        downloader.client = mock_client

        mock_response = MagicMock()
        mock_response.text = 'version="1.2.3"'
        mock_client.get.return_value = mock_response

        version = downloader.get_latest_version("someid")
        assert version == "1.2.3"
        mock_client.get.assert_called_once()

    def test_download(self, mock_client, tmp_path):
        downloader = ChromeDownloader()
        downloader.client = mock_client

        mock_client.download_file.return_value = tmp_path / "someid.crx"

        result = downloader.download("someid", tmp_path)
        assert result == tmp_path / "someid.crx"
        mock_client.download_file.assert_called_once()


class TestEdgeDownloaderNetwork:
    def test_get_latest_version(self, mock_client):
        downloader = EdgeDownloader()
        downloader.client = mock_client

        mock_response = MagicMock()
        mock_response.text = 'version="1.2.3"'
        mock_client.get.return_value = mock_response

        version = downloader.get_latest_version("someid")
        assert version == "1.2.3"
        mock_client.get.assert_called_once()

    def test_download(self, mock_client, tmp_path):
        downloader = EdgeDownloader()
        downloader.client = mock_client

        mock_client.download_file.return_value = tmp_path / "someid.crx"

        result = downloader.download("someid", tmp_path)
        assert result == tmp_path / "someid.crx"
        mock_client.download_file.assert_called_once()


class TestFirefoxDownloaderNetwork:
    def test_get_latest_version(self, mock_client):
        downloader = FirefoxDownloader()
        downloader.client = mock_client

        mock_response = MagicMock()
        mock_response.json.return_value = {"current_version": {"version": "1.2.3"}}
        mock_client.get.return_value = mock_response

        version = downloader.get_latest_version("someid")
        assert version == "1.2.3"
        mock_client.get.assert_called_once()

    def test_download(self, mock_client, tmp_path):
        downloader = FirefoxDownloader()
        downloader.client = mock_client

        # Mock metadata response
        mock_meta_response = MagicMock()
        mock_meta_response.json.return_value = {
            "current_version": {"file": {"url": "https://example.com/file.xpi"}}
        }
        mock_client.get.return_value = mock_meta_response

        mock_client.download_file.return_value = tmp_path / "file.xpi"

        result = downloader.download("someid", tmp_path)
        assert result == tmp_path / "file.xpi"
        mock_client.get.assert_called_once()
        mock_client.download_file.assert_called_once()
