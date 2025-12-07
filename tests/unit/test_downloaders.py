import pytest
from fetchext.downloaders.chrome import ChromeDownloader
from fetchext.downloaders.edge import EdgeDownloader
from fetchext.downloaders.firefox import FirefoxDownloader
from fetchext.exceptions import ExtensionError

class TestChromeDownloader:
    def test_extract_id_from_url(self):
        downloader = ChromeDownloader()
        url = "https://chromewebstore.google.com/detail/ublock-origin-lite/ddkjiahejlhfcafbddmgiahcphecmpfh"
        assert downloader.extract_id(url) == "ddkjiahejlhfcafbddmgiahcphecmpfh"

    def test_extract_id_from_id_string(self):
        downloader = ChromeDownloader()
        id_str = "ddkjiahejlhfcafbddmgiahcphecmpfh"
        assert downloader.extract_id(id_str) == "ddkjiahejlhfcafbddmgiahcphecmpfh"

    def test_extract_id_invalid(self):
        downloader = ChromeDownloader()
        with pytest.raises(ExtensionError):
            downloader.extract_id("https://google.com")

class TestEdgeDownloader:
    def test_extract_id_from_url(self):
        downloader = EdgeDownloader()
        url = "https://microsoftedge.microsoft.com/addons/detail/ublock-origin/odfafepnkmbhccpbejgmiehpchacaeak"
        assert downloader.extract_id(url) == "odfafepnkmbhccpbejgmiehpchacaeak"

    def test_extract_id_from_id_string(self):
        downloader = EdgeDownloader()
        id_str = "odfafepnkmbhccpbejgmiehpchacaeak"
        assert downloader.extract_id(id_str) == "odfafepnkmbhccpbejgmiehpchacaeak"

    def test_extract_id_invalid(self):
        downloader = EdgeDownloader()
        with pytest.raises(ExtensionError):
            downloader.extract_id("https://microsoft.com")

class TestFirefoxDownloader:
    def test_extract_id_from_url(self):
        downloader = FirefoxDownloader()
        url = "https://addons.mozilla.org/en-US/firefox/addon/ublock-origin/"
        assert downloader.extract_id(url) == "ublock-origin"

    def test_extract_id_from_url_no_slash(self):
        downloader = FirefoxDownloader()
        url = "https://addons.mozilla.org/en-US/firefox/addon/ublock-origin"
        assert downloader.extract_id(url) == "ublock-origin"

    def test_extract_id_invalid(self):
        downloader = FirefoxDownloader()
        with pytest.raises(ExtensionError):
            downloader.extract_id("https://mozilla.org")
