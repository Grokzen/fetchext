import pytest
import sys
from unittest.mock import patch
from fetchext.cli import main

class TestCLI:
    def test_help(self, capsys):
        with patch.object(sys, 'argv', ['fext', '--help']):
            with pytest.raises(SystemExit) as excinfo:
                main()
            assert excinfo.value.code == 0
            captured = capsys.readouterr()
            assert "Download or search for browser extensions" in captured.out

    def test_download_help(self, capsys):
        with patch.object(sys, 'argv', ['fext', 'download', '--help']):
            with pytest.raises(SystemExit) as excinfo:
                main()
            assert excinfo.value.code == 0
            captured = capsys.readouterr()
            assert "The browser type" in captured.out

    def test_no_args(self, capsys):
        with patch.object(sys, 'argv', ['fext']):
            with pytest.raises(SystemExit) as excinfo:
                main()
            assert excinfo.value.code != 0
            captured = capsys.readouterr()
            assert "the following arguments are required: command" in captured.err

    def test_invalid_command(self, capsys):
        with patch.object(sys, 'argv', ['fext', 'invalid']):
            with pytest.raises(SystemExit) as excinfo:
                main()
            assert excinfo.value.code != 0
            captured = capsys.readouterr()
            assert "invalid choice: 'invalid'" in captured.err

    def test_preview_command(self):
        with patch.object(sys, 'argv', ['fext', 'preview', 'test.crx']), \
             patch('fetchext.core.preview_extension') as mock_preview:
            main()
            mock_preview.assert_called_once_with('test.crx')

