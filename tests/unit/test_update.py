import pytest
from unittest.mock import patch, MagicMock
from fetchext.commands.update import handle_update
from fetchext.core.constants import ExitCode


@pytest.fixture
def mock_history():
    with patch("fetchext.commands.update.HistoryManager") as mock:
        yield mock


@pytest.fixture
def mock_download_extension():
    with patch("fetchext.commands.update.download_extension") as mock:
        yield mock


@pytest.fixture
def mock_downloader():
    with patch("fetchext.commands.update.get_downloader_for_browser") as mock_get:
        mock_cls = MagicMock()
        mock_instance = MagicMock()
        mock_cls.return_value = mock_instance
        mock_get.return_value = mock_cls
        yield mock_instance


def test_update_all_no_history(mock_history):
    mock_history.return_value.get_entries.return_value = []

    args = MagicMock()
    args.all = True

    handle_update(args)
    # Should just print "No download history found" and return


def test_update_all_up_to_date(mock_history, mock_downloader):
    entry = {
        "timestamp": "2023-01-01",
        "action": "download",
        "id": "abc",
        "version": "1.0.0",
        "browser": "chrome",
        "source": "http://example.com",
        "filename": "abc.crx",
    }
    mock_history.return_value.get_entries.return_value = [entry]
    mock_downloader.get_latest_version.return_value = "1.0.0"

    args = MagicMock()
    args.all = True
    args.dry_run = False

    handle_update(args)

    mock_downloader.get_latest_version.assert_called_with("abc")


def test_update_all_found_update(
    mock_history, mock_downloader, mock_download_extension
):
    entry = {
        "timestamp": "2023-01-01",
        "action": "download",
        "id": "abc",
        "version": "1.0.0",
        "browser": "chrome",
        "source": "http://example.com",
        "filename": "abc.crx",
    }
    mock_history.return_value.get_entries.return_value = [entry]
    mock_downloader.get_latest_version.return_value = "2.0.0"

    args = MagicMock()
    args.all = True
    args.dry_run = False

    handle_update(args)

    mock_download_extension.assert_called_once()
    call_args = mock_download_extension.call_args[1]
    assert call_args["browser"] == "chrome"
    assert call_args["url"] == "http://example.com"


def test_update_dry_run(mock_history, mock_downloader, mock_download_extension):
    entry = {
        "timestamp": "2023-01-01",
        "action": "download",
        "id": "abc",
        "version": "1.0.0",
        "browser": "chrome",
        "source": "http://example.com",
        "filename": "abc.crx",
    }
    mock_history.return_value.get_entries.return_value = [entry]
    mock_downloader.get_latest_version.return_value = "2.0.0"

    args = MagicMock()
    args.all = True
    args.dry_run = True

    handle_update(args)

    mock_download_extension.assert_not_called()


def test_update_requires_all_flag():
    args = MagicMock()
    args.all = False

    with pytest.raises(SystemExit) as exc:
        handle_update(args)
    assert exc.value.code == ExitCode.USAGE
