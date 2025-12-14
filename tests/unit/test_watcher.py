import pytest
from unittest.mock import Mock, patch
from fetchext.workflow.watcher import DirectoryWatcher, ExtensionEventHandler


@pytest.fixture
def mock_observer():
    with patch("fetchext.workflow.watcher.Observer") as mock:
        yield mock


@pytest.fixture
def mock_core():
    with (
        patch("fetchext.workflow.watcher.extract_extension") as mock_extract,
        patch("fetchext.workflow.watcher.generate_report") as mock_report,
        patch("fetchext.workflow.watcher.scan_extension") as mock_scan,
    ):
        yield mock_extract, mock_report, mock_scan


def test_event_handler_created_crx(mock_core):
    mock_extract, mock_report, mock_scan = mock_core
    handler = ExtensionEventHandler(actions=["extract", "report"])

    event = Mock()
    event.is_directory = False
    event.src_path = "/tmp/test.crx"

    with patch("time.sleep"):
        handler.on_created(event)

    mock_extract.assert_called_once()
    mock_report.assert_called_once()
    mock_scan.assert_not_called()


def test_event_handler_ignored_file(mock_core):
    mock_extract, _, _ = mock_core
    handler = ExtensionEventHandler(actions=["extract"])

    event = Mock()
    event.is_directory = False
    event.src_path = "/tmp/test.txt"

    handler.on_created(event)

    mock_extract.assert_not_called()


def test_watcher_start(mock_observer, tmp_path):
    watcher = DirectoryWatcher(tmp_path, actions=["extract"])

    # Mock infinite loop to break immediately
    with patch("time.sleep", side_effect=KeyboardInterrupt):
        watcher.start()

    mock_observer.return_value.schedule.assert_called_once()
    mock_observer.return_value.start.assert_called_once()
    mock_observer.return_value.stop.assert_called_once()
