import pytest
from pathlib import Path
from unittest.mock import MagicMock
from fetchext.network.network import download_file
from fetchext.core.exceptions import NetworkError


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.headers = {}
    return session


def test_download_file_new(fs, mock_session):
    """Test downloading a new file (no resume)."""
    output_path = Path("/tmp/test.crx")
    if not fs.exists("/tmp"):
        fs.create_dir("/tmp")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"content-length": "10"}
    mock_response.iter_content.return_value = [b"12345", b"67890"]
    mock_session.get.return_value = mock_response

    download_file(
        "http://example.com/test.crx",
        output_path,
        session=mock_session,
        show_progress=False,
    )

    assert output_path.exists()
    assert output_path.read_bytes() == b"1234567890"
    mock_session.get.assert_called_with(
        "http://example.com/test.crx", stream=True, headers={}, params=None
    )


def test_download_file_resume_success(fs, mock_session):
    """Test resuming a download with 206 Partial Content."""
    output_path = Path("/tmp/test.crx")
    if not fs.exists("/tmp"):
        fs.create_dir("/tmp")
    fs.create_file("/tmp/test.crx", contents=b"12345")

    mock_response = MagicMock()
    mock_response.status_code = 206
    mock_response.headers = {"content-length": "5"}  # Remaining bytes
    mock_response.iter_content.return_value = [b"67890"]
    mock_session.get.return_value = mock_response

    download_file(
        "http://example.com/test.crx",
        output_path,
        session=mock_session,
        show_progress=False,
    )

    assert output_path.read_bytes() == b"1234567890"
    # Verify Range header was sent
    args, kwargs = mock_session.get.call_args
    assert kwargs["headers"]["Range"] == "bytes=5-"


def test_download_file_resume_not_supported(fs, mock_session):
    """Test server returning 200 OK when resume requested (overwrite)."""
    output_path = Path("/tmp/test.crx")
    if not fs.exists("/tmp"):
        fs.create_dir("/tmp")
    fs.create_file("/tmp/test.crx", contents=b"partial")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"content-length": "10"}
    mock_response.iter_content.return_value = [b"12345", b"67890"]
    mock_session.get.return_value = mock_response

    download_file(
        "http://example.com/test.crx",
        output_path,
        session=mock_session,
        show_progress=False,
    )

    assert output_path.read_bytes() == b"1234567890"
    # Verify Range header was sent but ignored by server logic (overwritten locally)
    args, kwargs = mock_session.get.call_args
    assert kwargs["headers"]["Range"] == "bytes=7-"


def test_download_file_416_range_not_satisfiable(fs, mock_session):
    """Test handling 416 Range Not Satisfiable (restart download)."""
    output_path = Path("/tmp/test.crx")
    if not fs.exists("/tmp"):
        fs.create_dir("/tmp")
    fs.create_file("/tmp/test.crx", contents=b"invalid_partial")

    # First call returns 416
    mock_response_416 = MagicMock()
    mock_response_416.status_code = 416

    # Second call returns 200 (full download)
    mock_response_200 = MagicMock()
    mock_response_200.status_code = 200
    mock_response_200.headers = {"content-length": "5"}
    mock_response_200.iter_content.return_value = [b"fresh"]

    mock_session.get.side_effect = [mock_response_416, mock_response_200]

    download_file(
        "http://example.com/test.crx",
        output_path,
        session=mock_session,
        show_progress=False,
    )

    assert output_path.read_bytes() == b"fresh"
    assert mock_session.get.call_count == 2
    # First call had Range
    assert mock_session.get.call_args_list[0][1]["headers"]["Range"] == "bytes=15-"
    # Second call had no Range
    assert "Range" not in mock_session.get.call_args_list[1][1]["headers"]


def test_download_file_empty_cleanup(fs, mock_session):
    """Test that empty files are cleaned up on failure."""
    output_path = Path("/tmp/test.crx")
    if not fs.exists("/tmp"):
        fs.create_dir("/tmp")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"content-length": "0"}
    mock_response.iter_content.return_value = []
    mock_session.get.return_value = mock_response

    with pytest.raises(NetworkError, match="File is empty"):
        download_file(
            "http://example.com/test.crx",
            output_path,
            session=mock_session,
            show_progress=False,
        )

    assert not output_path.exists()
