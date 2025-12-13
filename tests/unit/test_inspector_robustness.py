import pytest
from unittest.mock import MagicMock, patch
import json
from fetchext.inspector import ExtensionInspector

@pytest.fixture
def inspector():
    return ExtensionInspector()

def test_inspect_valid(inspector):
    mock_zip = MagicMock()
    
    # Timeline setup
    info1 = MagicMock()
    info1.filename = "manifest.json"
    info1.date_time = (2023, 1, 1, 12, 0, 0)
    info1.file_size = 100
    mock_zip.infolist.return_value = [info1]
    
    # Manifest setup
    mock_zip.namelist.return_value = ["manifest.json"]
    
    # Mock file context manager
    mock_file = MagicMock()
    mock_open_file = MagicMock()
    mock_open_file.__enter__.return_value = mock_file
    mock_zip.open.return_value = mock_open_file
    
    with patch("fetchext.inspector.open_extension_archive") as mock_open:
        mock_open.return_value.__enter__.return_value = mock_zip
        # Patch json.load to return a dict
        with patch("json.load", return_value={"name": "Test"}):
             result = inspector.inspect("dummy.crx")
        
        assert result["valid"] is True
        assert result["manifest"] == {"name": "Test"}
        assert len(result["timeline"]) == 1
        assert len(result["errors"]) == 0

def test_inspect_missing_manifest(inspector):
    mock_zip = MagicMock()
    mock_zip.infolist.return_value = []
    mock_zip.namelist.return_value = ["other.js"]
    
    with patch("fetchext.inspector.open_extension_archive") as mock_open:
        mock_open.return_value.__enter__.return_value = mock_zip
        
        result = inspector.inspect("dummy.crx")
        
        assert result["valid"] is False
        assert result["manifest"] is None
        assert "manifest.json not found in archive" in result["errors"]

def test_inspect_invalid_manifest_json(inspector):
    mock_zip = MagicMock()
    mock_zip.infolist.return_value = []
    mock_zip.namelist.return_value = ["manifest.json"]
    
    mock_file = MagicMock()
    mock_open_file = MagicMock()
    mock_open_file.__enter__.return_value = mock_file
    mock_zip.open.return_value = mock_open_file
    
    with patch("fetchext.inspector.open_extension_archive") as mock_open:
        mock_open.return_value.__enter__.return_value = mock_zip
        
        # json.load raises JSONDecodeError
        with patch("json.load", side_effect=json.JSONDecodeError("Expecting value", "", 0)):
            result = inspector.inspect("dummy.crx")
            
        assert result["valid"] is False
        assert result["manifest"] is None
        assert any("Manifest JSON invalid" in e for e in result["errors"])

def test_inspect_corrupt_archive(inspector):
    with patch("fetchext.inspector.open_extension_archive", side_effect=Exception("Corrupt")):
        result = inspector.inspect("bad.crx")
        
        assert result["valid"] is False
        assert any("Archive open failed" in e for e in result["errors"])
