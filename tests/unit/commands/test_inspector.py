import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from fetchext.inspector import ExtensionInspector

@pytest.fixture
def inspector():
    return ExtensionInspector()

def test_get_timeline(inspector):
    # Mock the zip file object and its infolist method
    mock_zip = MagicMock()
    
    # Create mock ZipInfo objects
    info1 = MagicMock()
    info1.filename = "file1.js"
    info1.date_time = (2023, 1, 1, 12, 0, 0)
    info1.file_size = 100
    
    info2 = MagicMock()
    info2.filename = "file2.css"
    info2.date_time = (2023, 1, 2, 14, 30, 0)
    info2.file_size = 200
    
    mock_zip.infolist.return_value = [info2, info1] # Unsorted
    
    # Mock open_extension_archive to return our mock zip
    with patch("fetchext.inspector.open_extension_archive") as mock_open:
        mock_open.return_value.__enter__.return_value = mock_zip
        
        timeline = inspector.get_timeline("dummy.crx")
        
        assert len(timeline) == 2
        # Check sorting (should be by date)
        assert timeline[0]["filename"] == "file1.js"
        assert timeline[0]["datetime"] == datetime(2023, 1, 1, 12, 0, 0)
        
        assert timeline[1]["filename"] == "file2.css"
        assert timeline[1]["datetime"] == datetime(2023, 1, 2, 14, 30, 0)

def test_get_timeline_error(inspector):
    with patch("fetchext.inspector.open_extension_archive", side_effect=Exception("Corrupt file")):
        with pytest.raises(ValueError, match="Could not read archive for timeline"):
            inspector.get_timeline("bad.crx")
