from unittest.mock import Mock
import fetchext


def test_public_api_exports():
    """Verify that key functions are exported in the top-level package."""
    assert hasattr(fetchext, "download_extension")
    assert hasattr(fetchext, "search_extension")
    assert hasattr(fetchext, "inspect_extension")
    assert hasattr(fetchext, "extract_extension")
    assert hasattr(fetchext, "batch_download")


def test_download_extension_call(mocker):
    """Verify download_extension calls the correct downloader."""
    mock_downloader = mocker.Mock()
    mock_downloader.extract_id.return_value = "test_id"
    mock_downloader.download.return_value = Mock(name="path")

    mocker.patch("fetchext.core.ChromeDownloader", return_value=mock_downloader)

    fetchext.download_extension("chrome", "http://example.com", "/tmp")

    mock_downloader.extract_id.assert_called_with("http://example.com")
    mock_downloader.download.assert_called()


def test_search_extension_call(mocker):
    """Verify search_extension calls the correct downloader."""
    mock_downloader = mocker.Mock()
    mock_downloader.search.return_value = []  # Return empty list
    mocker.patch("fetchext.core.FirefoxDownloader", return_value=mock_downloader)

    # Mock cache to always miss
    mock_cache = mocker.Mock()
    mock_cache.get.return_value = None
    mocker.patch("fetchext.core.SearchCache", return_value=mock_cache)

    fetchext.search_extension("firefox", "query")

    mock_downloader.search.assert_called_with("query")
