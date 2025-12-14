from pathlib import Path
from fetchext.cli import main
from unittest.mock import patch
import pytest


def test_report_command(fs, capsys):
    # Create a fake CRX file
    fake_crx = Path("extension.crx")
    fs.create_file(fake_crx, contents="fake content")

    # Mock core.generate_report
    with patch("fetchext.core.core.generate_report") as mock_generate:
        with patch("sys.argv", ["fext", "report", "extension.crx"]):
            with pytest.raises(SystemExit) as excinfo:
                main()
            assert excinfo.value.code == 0

        mock_generate.assert_called_once()
        args, _ = mock_generate.call_args
        assert args[0] == "extension.crx"
        assert args[1] is None


def test_report_command_with_output(fs, capsys):
    fake_crx = Path("extension.crx")
    fs.create_file(fake_crx, contents="fake content")

    with patch("fetchext.core.core.generate_report") as mock_generate:
        with patch(
            "sys.argv", ["fext", "report", "extension.crx", "-o", "my_report.md"]
        ):
            with pytest.raises(SystemExit) as excinfo:
                main()
            assert excinfo.value.code == 0

        mock_generate.assert_called_once()
        args, _ = mock_generate.call_args
        assert args[0] == "extension.crx"
        assert args[1] == Path("my_report.md")
