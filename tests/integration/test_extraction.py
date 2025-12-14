import zipfile
import pytest
from pathlib import Path
from fetchext.cli import main
from unittest.mock import patch


def test_auto_extraction(fs, mocker):
    # Mock downloader
    mock_downloader_cls = mocker.patch("fetchext.core.ChromeDownloader")
    mock_downloader = mock_downloader_cls.return_value
    mock_downloader.extract_id.return_value = "test_id"

    # Create a fake downloaded file (zip)
    output_dir = Path("/downloads")
    output_dir.mkdir()
    fake_crx = output_dir / "test_id.crx"

    # Create a valid zip file on the fake filesystem
    with zipfile.ZipFile(fake_crx, "w") as zf:
        zf.writestr("manifest.json", '{"name": "Test"}')
        zf.writestr("script.js", "console.log('hello')")

    mock_downloader.download.return_value = fake_crx

    # Run CLI with --extract
    with patch(
        "sys.argv",
        [
            "fext",
            "download",
            "chrome",
            "http://example.com",
            "-o",
            "/downloads",
            "--extract",
        ],
    ):
        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 0

    # Check if extracted directory exists
    # The CLI uses output_path.stem as the directory name
    # output_path is /downloads/test_id.crx, stem is test_id
    extract_dir = output_dir / "test_id"
    assert extract_dir.exists()
    assert extract_dir.is_dir()
    assert (extract_dir / "manifest.json").exists()
    assert (extract_dir / "script.js").exists()


def test_extract_command(fs):
    # Create a fake zip file
    file_path = Path("test.crx")
    with zipfile.ZipFile(file_path, "w") as zf:
        zf.writestr("manifest.json", "{}")

    # Run extract command
    with patch("sys.argv", ["fext", "extract", "test.crx"]):
        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 0

    # Check default output dir
    assert Path("test").exists()
    assert (Path("test") / "manifest.json").exists()


def test_extract_command_custom_output(fs):
    # Create a fake zip file
    file_path = Path("test.crx")
    with zipfile.ZipFile(file_path, "w") as zf:
        zf.writestr("manifest.json", "{}")

    # Run extract command with -o
    with patch("sys.argv", ["fext", "extract", "test.crx", "-o", "custom_dir"]):
        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 0

    # Check custom output dir
    assert Path("custom_dir").exists()
    assert (Path("custom_dir") / "manifest.json").exists()
