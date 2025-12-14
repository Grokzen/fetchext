import pytest
from unittest.mock import MagicMock, patch, mock_open
from pathlib import Path
import sys

# Mock yara module before importing the class under test
sys.modules["yara"] = MagicMock()
import yara  # noqa: E402, F401

from fetchext.analysis.yara import YaraScanner  # noqa: E402


@pytest.fixture
def mock_yara_compile():
    with patch("yara.compile") as mock:
        yield mock


def test_yara_scanner_init(mock_yara_compile):
    rules_path = Path("rules.yar")
    with patch("pathlib.Path.exists", return_value=True):
        scanner = YaraScanner(rules_path)
        mock_yara_compile.assert_called_once_with(filepath="rules.yar")
        assert scanner.rules == mock_yara_compile.return_value


def test_yara_scanner_init_file_not_found():
    rules_path = Path("nonexistent.yar")
    with patch("pathlib.Path.exists", return_value=False):
        with pytest.raises(FileNotFoundError):
            YaraScanner(rules_path)


def test_scan_content(mock_yara_compile):
    rules_path = Path("rules.yar")
    with patch("pathlib.Path.exists", return_value=True):
        scanner = YaraScanner(rules_path)

        # Mock match return
        mock_match = MagicMock()
        mock_match.rule = "TestRule"
        mock_match.tags = ["malware"]
        mock_match.meta = {"author": "me"}
        mock_match.strings = []

        scanner.rules.match.return_value = [mock_match]

        content = b"malicious content"
        matches = scanner.scan_content(content, "test.js")

        assert len(matches) == 1
        assert matches[0]["rule"] == "TestRule"
        assert matches[0]["filename"] == "test.js"
        scanner.rules.match.assert_called_once_with(data=content)


def test_scan_archive(mock_yara_compile):
    rules_path = Path("rules.yar")
    with patch("pathlib.Path.exists", return_value=True):
        scanner = YaraScanner(rules_path)

        # Mock match return
        mock_match = MagicMock()
        mock_match.rule = "TestRule"

        scanner.rules.match.return_value = [mock_match]

        # Mock ZipFile
        with patch("fetchext.analysis.yara.ZipFile") as MockZipFile:
            mock_zip = MockZipFile.return_value
            mock_zip.__enter__.return_value = mock_zip

            # Mock infolist
            mock_info = MagicMock()
            mock_info.filename = "malware.js"
            mock_info.file_size = 100  # Small file
            mock_info.is_dir.return_value = False
            mock_zip.infolist.return_value = [mock_info]

            # Mock read
            mock_zip.read.return_value = b"content"

            # Mock open
            with patch("builtins.open", mock_open(read_data=b"zipdata")):
                # Mock CrxDecoder
                with patch(
                    "fetchext.analysis.yara.CrxDecoder.get_zip_offset", return_value=0
                ):
                    results = scanner.scan_archive(Path("test.crx"))

                    assert "malware.js" in results
                    assert len(results["malware.js"]) == 1
                    assert results["malware.js"][0]["rule"] == "TestRule"
