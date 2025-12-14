from unittest.mock import patch, MagicMock
from fetchext.core import search_extension


def test_search_uses_cache():
    with (
        patch("fetchext.core.SearchCache") as MockCache,
        patch("fetchext.core.get_downloader") as mock_get_downloader,
    ):
        mock_downloader = MagicMock()
        mock_downloader.search.return_value = [{"id": "remote"}]
        mock_get_downloader.return_value = mock_downloader

        mock_cache_instance = MockCache.return_value
        mock_cache_instance.get.return_value = [{"id": "cached"}]

        # 1. Cache hit
        results = search_extension("chrome", "query")
        assert results == [{"id": "cached"}]
        mock_downloader.search.assert_not_called()

        # 2. Cache miss
        mock_cache_instance.get.return_value = None
        results = search_extension("chrome", "query")
        assert results == [{"id": "remote"}]
        mock_downloader.search.assert_called_once_with("query")
        mock_cache_instance.set.assert_called_once_with(
            "chrome", "query", [{"id": "remote"}]
        )


def test_search_refresh_ignores_cache():
    with (
        patch("fetchext.core.SearchCache") as MockCache,
        patch("fetchext.core.get_downloader") as mock_get_downloader,
    ):
        mock_downloader = MagicMock()
        mock_downloader.search.return_value = [{"id": "remote"}]
        mock_get_downloader.return_value = mock_downloader

        mock_cache_instance = MockCache.return_value
        mock_cache_instance.get.return_value = [{"id": "cached"}]

        # Refresh=True
        results = search_extension("chrome", "query", refresh=True)
        assert results == [{"id": "remote"}]
        mock_downloader.search.assert_called_once_with("query")
        # Should still update cache
        mock_cache_instance.set.assert_called_once_with(
            "chrome", "query", [{"id": "remote"}]
        )
