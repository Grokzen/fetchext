import pytest
from unittest.mock import MagicMock, patch
from fetchext import core
from fetchext.downloaders.base import BaseDownloader


@pytest.fixture
def mock_downloader():
    downloader = MagicMock(spec=BaseDownloader)
    downloader.get_latest_version.return_value = "2.0.0"
    return downloader


@pytest.fixture
def mock_get_downloader(mock_downloader):
    with patch("fetchext.core.core.get_downloader") as mock:
        mock.return_value = mock_downloader
        yield mock


def test_check_update_with_metadata_file(fs, mock_get_downloader, capsys):
    # Setup
    fs.create_file("extension.crx")
    fs.create_file(
        "extension.crx.json",
        contents='{"id": "test-id", "version": "1.0.0", "browser": "chrome"}',
    )

    # Mock ExtensionInspector to avoid file parsing error
    with patch("fetchext.core.core.ExtensionInspector") as MockInspector:
        mock_instance = MockInspector.return_value
        mock_instance.get_manifest.return_value = {
            "version": "1.0.0",
            "browser_specific_settings": {"gecko": {"id": "test-id"}},
        }

        # Execute
        core.check_update("extension.crx")

    # Verify
    captured = capsys.readouterr()
    assert "Update Available!" in captured.out
    assert "1.0.0 -> 2.0.0" in captured.out
    mock_get_downloader.assert_called_with("chrome")
    mock_get_downloader.return_value.get_latest_version.assert_called_with("test-id")


def test_check_update_no_update(fs, mock_get_downloader, capsys):
    # Setup
    fs.create_file("extension.crx")
    fs.create_file(
        "extension.crx.json",
        contents='{"id": "test-id", "version": "2.0.0", "browser": "chrome"}',
    )

    with patch("fetchext.core.core.ExtensionInspector") as MockInspector:
        mock_instance = MockInspector.return_value
        mock_instance.get_manifest.return_value = {"version": "2.0.0"}

        # Execute
        core.check_update("extension.crx")

    # Verify
    captured = capsys.readouterr()
    assert "Up to date." in captured.out
    assert "(2.0.0)" in captured.out


def test_check_update_json_output(fs, mock_get_downloader, capsys):
    # Setup
    fs.create_file("extension.crx")
    fs.create_file(
        "extension.crx.json",
        contents='{"id": "test-id", "version": "1.0.0", "browser": "chrome"}',
    )

    with patch("fetchext.core.core.ExtensionInspector") as MockInspector:
        mock_instance = MockInspector.return_value
        mock_instance.get_manifest.return_value = {"version": "1.0.0"}

        # Execute
        core.check_update("extension.crx", json_output=True)

    # Verify
    captured = capsys.readouterr()
    assert '"update_available": true' in captured.out
    assert '"remote_version": "2.0.0"' in captured.out


def test_check_update_infer_from_manifest(fs, mock_get_downloader, capsys):
    # Setup
    fs.create_file("extension.crx")
    # Mock ExtensionInspector to return manifest info
    with patch("fetchext.core.core.ExtensionInspector") as MockInspector:
        mock_instance = MockInspector.return_value
        mock_instance.get_manifest.return_value = {
            "name": "Test Ext",
            "version": "1.0.0",
            "browser_specific_settings": {"gecko": {"id": "inferred-id"}},
        }

        # Execute
        core.check_update("extension.crx")

        # Verify
        mock_get_downloader.assert_called_with("firefox")
        mock_get_downloader.return_value.get_latest_version.assert_called_with(
            "inferred-id"
        )


def test_check_update_cannot_determine_id(fs, capsys):
    # Setup
    fs.create_file("extension.crx")

    # Mock ExtensionInspector to return manifest without ID
    with patch("fetchext.core.core.ExtensionInspector") as MockInspector:
        mock_instance = MockInspector.return_value
        mock_instance.get_manifest.return_value = {
            "name": "Test Ext",
            "version": "1.0.0",
        }

        # Execute
        with pytest.raises(ValueError):
            core.check_update("extension.crx")

        # Verify
        capsys.readouterr()


def test_check_update_error_fetching_version(fs, mock_get_downloader, capsys):
    # Setup
    fs.create_file("extension.crx")
    fs.create_file(
        "extension.crx.json",
        contents='{"id": "test-id", "version": "1.0.0", "browser": "chrome"}',
    )

    mock_get_downloader.return_value.get_latest_version.side_effect = Exception(
        "Network error"
    )

    with patch("fetchext.core.core.ExtensionInspector") as MockInspector:
        mock_instance = MockInspector.return_value
        mock_instance.get_manifest.return_value = {"version": "1.0.0"}

        # Execute
        with pytest.raises(Exception, match="Network error"):
            core.check_update("extension.crx")
