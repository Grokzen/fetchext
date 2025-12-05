import pytest
import json
from unittest.mock import MagicMock, patch
from fetchext.auditor import ExtensionAuditor

@pytest.fixture
def mock_zip_file():
    zf = MagicMock()
    # Default manifest
    manifest = {
        "manifest_version": 2,
        "name": "Test Extension",
        "version": "1.0",
        "browser_action": {},
        "background": {"scripts": ["bg.js"]}
    }
    zf.read.side_effect = lambda name: json.dumps(manifest).encode() if name == "manifest.json" else b""
    zf.namelist.return_value = ["manifest.json", "bg.js"]
    return zf

def test_audit_mv2_extension(mock_zip_file):
    with patch("fetchext.auditor.open_extension_archive") as mock_open:
        mock_open.return_value.__enter__.return_value = mock_zip_file
        
        auditor = ExtensionAuditor()
        report = auditor.audit("dummy.crx")
        
        assert report.manifest_version == 2
        assert not report.is_mv3
        
        # Check issues
        messages = [i.message for i in report.issues]
        assert "Extension is using Manifest V2, which is deprecated." in messages
        assert "'browser_action' is deprecated in MV3. Use 'action' instead." in messages
        assert "Persistent background pages ('background.scripts') are replaced by Service Workers in MV3." in messages

def test_audit_mv3_extension():
    zf = MagicMock()
    manifest = {
        "manifest_version": 3,
        "name": "MV3 Extension",
        "version": "1.0",
        "action": {},
        "background": {"service_worker": "sw.js"}
    }
    zf.read.side_effect = lambda name: json.dumps(manifest).encode() if name == "manifest.json" else b""
    zf.namelist.return_value = ["manifest.json", "sw.js"]
    
    with patch("fetchext.auditor.open_extension_archive") as mock_open:
        mock_open.return_value.__enter__.return_value = zf
        
        auditor = ExtensionAuditor()
        report = auditor.audit("dummy.crx")
        
        assert report.manifest_version == 3
        assert report.is_mv3
        
        messages = [i.message for i in report.issues]
        assert "Extension is using Manifest V3." in messages
        # Should be no warnings about browser_action etc.
        assert not any("deprecated" in m for m in messages if "Manifest V2" not in m)

def test_audit_code_scan():
    zf = MagicMock()
    manifest = {"manifest_version": 3}
    zf.read.side_effect = lambda name: \
        json.dumps(manifest).encode() if name == "manifest.json" else \
        b"chrome.browserAction.setIcon({});\nchrome.webRequest.onBeforeRequest.addListener();"
    
    zf.namelist.return_value = ["manifest.json", "script.js"]
    
    with patch("fetchext.auditor.open_extension_archive") as mock_open:
        mock_open.return_value.__enter__.return_value = zf
        
        auditor = ExtensionAuditor()
        report = auditor.audit("dummy.crx")
        
        messages = [i.message for i in report.issues]
        assert any("chrome.browserAction is deprecated" in m for m in messages)
        assert any("chrome.webRequest blocking is limited" in m for m in messages)
