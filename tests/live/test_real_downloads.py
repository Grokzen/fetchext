import pytest
from fetchext.downloaders.chrome import ChromeDownloader
from fetchext.downloaders.edge import EdgeDownloader
from fetchext.downloaders.firefox import FirefoxDownloader


@pytest.mark.live
class TestRealDownloads:
    def test_chrome_real_download(self, tmp_path):
        downloader = ChromeDownloader()
        # Postman Interceptor ID
        extension_id = "aicmkgpgakddgnaphhhpliifpcfhicfo"
        output_path = downloader.download(extension_id, tmp_path)

        assert output_path.exists()
        assert output_path.stat().st_size > 0
        assert output_path.suffix == ".crx"

    def test_edge_real_download(self, tmp_path):
        downloader = EdgeDownloader()
        # Postman Interceptor ID
        extension_id = "nbjbemmokmdpdokpnbfpdfbikmhgilmc"
        output_path = downloader.download(extension_id, tmp_path)

        assert output_path.exists()
        assert output_path.stat().st_size > 0
        assert output_path.suffix == ".crx"

    def test_firefox_real_download(self, tmp_path):
        downloader = FirefoxDownloader()
        # Postman Interceptor Slug
        extension_id = "postman_interceptor"
        output_path = downloader.download(extension_id, tmp_path)

        assert output_path.exists()
        assert output_path.stat().st_size > 0
        assert output_path.suffix == ".xpi"
