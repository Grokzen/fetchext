import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from fetchext.security.secrets import SecretScanner


@pytest.fixture
def scanner():
    return SecretScanner()


def test_scan_content_aws(scanner):
    content = "var key = 'AKIAIOSFODNN7EXAMPLE';"
    findings = scanner._scan_line(content, "test.js", 1)
    assert len(findings) == 1
    assert findings[0].type == "AWS Access Key"
    assert findings[0].match.startswith("AKIA")
    assert "*" in findings[0].match


def test_scan_content_google(scanner):
    # Ensure key is long enough (39 chars total: AIza + 35 chars)
    # AIza + 35 'a's
    key = "AIza" + "a" * 35
    content = f"const apiKey = '{key}';"
    findings = scanner._scan_line(content, "config.js", 1)
    assert len(findings) == 1
    assert findings[0].type == "Google API Key"


def test_scan_content_generic(scanner):
    content = "api_key = '12345678901234567890';"
    findings = scanner._scan_line(content, "settings.py", 1)
    assert len(findings) == 1
    assert findings[0].type == "Generic API Key"


def test_scan_content_no_secrets(scanner):
    content = "var x = 1; // No secrets here"
    findings = scanner._scan_line(content, "safe.js", 1)
    assert len(findings) == 0


@patch("fetchext.security.secrets.open_extension_archive")
def test_scan_extension(mock_open, scanner):
    # Mock zip file
    mock_zf = MagicMock()
    mock_zf.namelist.return_value = ["script.js", "image.png"]

    # Mock file context manager
    mock_file = MagicMock()
    mock_file.__enter__.return_value = [b"var token = 'xoxb-1234567890-1234567890';"]
    mock_file.__exit__.return_value = None

    mock_zf.open.return_value = mock_file

    mock_open.return_value.__enter__.return_value = mock_zf

    findings = scanner.scan_extension(Path("dummy.crx"))

    assert len(findings) == 1
    assert findings[0].type == "Slack Token"
    assert findings[0].file == "script.js"

    # Verify image was skipped (open called only once for script.js)
    mock_zf.open.assert_called_once_with("script.js")
