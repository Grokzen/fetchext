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
            with pytest.raises(SystemExit) as excinfo:
                main()
            assert excinfo.value.code == 0
            mock_preview.assert_called_once_with('test.crx')

    def test_audit_command(self):
        with patch.object(sys, 'argv', ['fext', 'audit', 'test.crx']), \
             patch('fetchext.core.audit_extension') as mock_audit:
            with pytest.raises(SystemExit) as excinfo:
                main()
            assert excinfo.value.code == 0
            mock_audit.assert_called_once_with('test.crx', json_output=False)

    def test_diff_command(self):
        with patch.object(sys, 'argv', ['fext', 'diff', 'old.crx', 'new.crx']), \
             patch('fetchext.core.diff_extensions') as mock_diff:
            with pytest.raises(SystemExit) as excinfo:
                main()
            assert excinfo.value.code == 0
            mock_diff.assert_called_once_with('old.crx', 'new.crx', json_output=False, ignore_whitespace=False)

    def test_risk_command(self):
        with patch.object(sys, 'argv', ['fext', 'risk', 'test.crx']), \
             patch('fetchext.core.analyze_risk') as mock_risk:
            with pytest.raises(SystemExit) as excinfo:
                main()
            assert excinfo.value.code == 0
            mock_risk.assert_called_once_with('test.crx', json_output=False)

    def test_verify_command(self):
        with patch.object(sys, 'argv', ['fext', 'verify', 'test.crx']), \
             patch('fetchext.core.verify_signature') as mock_verify:
            mock_verify.return_value = True
            with pytest.raises(SystemExit) as excinfo:
                main()
            assert excinfo.value.code == 0
            mock_verify.assert_called_once_with('test.crx', json_output=False)





