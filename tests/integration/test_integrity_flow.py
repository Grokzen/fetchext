import pytest
from pathlib import Path
from fetchext.core.core import download_extension
from fetchext.core.exceptions import IntegrityError


class TestIntegrityIntegration:
    def test_download_with_correct_hash(self, fs, mocker):
        # Mock downloader
        mock_downloader = mocker.Mock()
        mock_downloader.extract_id.return_value = "abc"
        mock_downloader.download.return_value = Path("/tmp/abc.crx")

        mocker.patch("fetchext.core.core.get_downloader", return_value=mock_downloader)

        # Create dummy file
        fs.create_file("/tmp/abc.crx", contents=b"content")
        import hashlib

        correct_hash = hashlib.sha256(b"content").hexdigest()

        output_path = download_extension(
            "chrome",
            "http://example.com",
            "/tmp",
            verify_hash=correct_hash,
            show_progress=False,
        )

        assert output_path.exists()

    def test_download_with_incorrect_hash_cleanup(self, fs, mocker):
        # Mock downloader
        mock_downloader = mocker.Mock()
        mock_downloader.extract_id.return_value = "abc"
        mock_downloader.download.return_value = Path("/tmp/abc.crx")

        mocker.patch("fetchext.core.core.get_downloader", return_value=mock_downloader)

        # Create dummy file
        fs.create_file("/tmp/abc.crx", contents=b"content")
        wrong_hash = "a" * 64

        with pytest.raises(IntegrityError):
            download_extension(
                "chrome",
                "http://example.com",
                "/tmp",
                verify_hash=wrong_hash,
                show_progress=False,
            )

        # Verify file was deleted
        assert not Path("/tmp/abc.crx").exists()
