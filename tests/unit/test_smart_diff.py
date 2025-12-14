import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from fetchext.workflow.diff import ExtensionDiffer


@pytest.fixture
def differ():
    return ExtensionDiffer()


@patch("fetchext.workflow.diff.open_extension_archive")
def test_diff_ignore_whitespace(mock_open, differ):
    # Setup mocks
    mock_old_zf = MagicMock()
    mock_new_zf = MagicMock()

    # Configure context managers to return the mocks themselves
    mock_old_zf.__enter__.return_value = mock_old_zf
    mock_new_zf.__enter__.return_value = mock_new_zf

    mock_open.side_effect = [mock_old_zf, mock_new_zf]

    # Mock manifest
    mock_old_zf.read.side_effect = (
        lambda f: b'{"version": "1.0"}' if f == "manifest.json" else b"var x = 1;"
    )
    mock_new_zf.read.side_effect = (
        lambda f: b'{"version": "1.0"}' if f == "manifest.json" else b"var x=1;"
    )  # Whitespace change

    # Mock file info
    info_old = MagicMock()
    info_old.filename = "script.js"
    info_old.CRC = 123
    info_old.file_size = 10

    info_new = MagicMock()
    info_new.filename = "script.js"
    info_new.CRC = 456  # Different CRC
    info_new.file_size = 9

    mock_old_zf.infolist.return_value = [info_old]
    mock_new_zf.infolist.return_value = [info_new]

    # Test WITHOUT ignore_whitespace
    report = differ.diff(Path("old.zip"), Path("new.zip"), ignore_whitespace=False)
    assert "script.js" in report.modified_files

    # Reset mocks for second run
    mock_open.side_effect = [mock_old_zf, mock_new_zf]
    # Reset read side effect because it might have been exhausted or we want to ensure consistency
    mock_old_zf.read.side_effect = (
        lambda f: b'{"version": "1.0"}' if f == "manifest.json" else b"var x = 1;"
    )
    mock_new_zf.read.side_effect = (
        lambda f: b'{"version": "1.0"}' if f == "manifest.json" else b"var x=1;"
    )

    # Test WITH ignore_whitespace
    report = differ.diff(Path("old.zip"), Path("new.zip"), ignore_whitespace=True)
    assert "script.js" not in report.modified_files


@patch("fetchext.workflow.diff.open_extension_archive")
@patch("fetchext.workflow.diff.Image.open")
def test_diff_images(mock_img_open, mock_open, differ):
    # Setup mocks
    mock_old_zf = MagicMock()
    mock_new_zf = MagicMock()

    mock_old_zf.__enter__.return_value = mock_old_zf
    mock_new_zf.__enter__.return_value = mock_new_zf

    mock_open.side_effect = [mock_old_zf, mock_new_zf]

    # Mock manifest
    mock_old_zf.read.side_effect = (
        lambda f: b'{"version": "1.0"}' if f == "manifest.json" else b"image_bytes_old"
    )
    mock_new_zf.read.side_effect = (
        lambda f: b'{"version": "1.0"}' if f == "manifest.json" else b"image_bytes_new"
    )

    # Mock file info
    info_old = MagicMock()
    info_old.filename = "icon.png"
    info_old.CRC = 111
    info_old.file_size = 100

    info_new = MagicMock()
    info_new.filename = "icon.png"
    info_new.CRC = 222
    info_new.file_size = 200

    mock_old_zf.infolist.return_value = [info_old]
    mock_new_zf.infolist.return_value = [info_new]

    # Mock Image objects
    img_old = MagicMock()
    img_old.size = (100, 100)
    img_old.mode = "RGB"
    img_old.format = "PNG"

    img_new = MagicMock()
    img_new.size = (200, 200)  # Changed size
    img_new.mode = "RGB"
    img_new.format = "PNG"

    mock_img_open.side_effect = [img_old, img_new]

    report = differ.diff(Path("old.zip"), Path("new.zip"))

    assert "icon.png" in report.modified_files
    assert len(report.image_changes) == 1
    assert report.image_changes[0]["file"] == "icon.png"
    assert report.image_changes[0]["diff"]["size"] == "(100, 100) -> (200, 200)"
