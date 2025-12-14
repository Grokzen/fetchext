from unittest.mock import patch
from fetchext.cli import main


def test_cli_help_snapshot(capsys, snapshot):
    with patch("sys.argv", ["fext", "--help"]):
        try:
            main()
        except SystemExit:
            pass

    captured = capsys.readouterr()
    assert captured.out == snapshot


def test_cli_version_snapshot(capsys, snapshot):
    with patch("sys.argv", ["fext", "--version"]):
        try:
            main()
        except SystemExit:
            pass

    captured = capsys.readouterr()
    # Version changes, so we might need to sanitize or just check structure
    # But for now let's snapshot it. If version changes, snapshot updates.
    assert captured.out == snapshot


def test_cli_info_snapshot(capsys, snapshot, tmp_path):
    # Create a dummy extension file
    ext_file = tmp_path / "test.crx"
    ext_file.touch()

    with (
        patch("sys.argv", ["fext", "info", str(ext_file)]),
        patch(
            "fetchext.core.get_extension_info",
            return_value={"id": "abc", "version": "1.0"},
        ),
    ):
        try:
            main()
        except SystemExit:
            pass

    captured = capsys.readouterr()
    assert captured.out == snapshot
