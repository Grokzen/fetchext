import csv
from io import StringIO
from unittest.mock import MagicMock, patch
from fetchext.core import search_extension, scan_extension
from fetchext.scanner import ScanReport, DetectedLibrary

def test_search_csv_export():
    mock_downloader = MagicMock()
    mock_downloader.search.return_value = [
        {
            "id": "123",
            "name": "Test Ext",
            "version": "1.0",
            "url": "http://example.com",
            "description": "Desc",
            "users": "100",
            "rating": "4.5"
        }
    ]
    
    with patch("fetchext.core.get_downloader", return_value=mock_downloader):
        with patch("fetchext.core.SearchCache") as MockCache:
            MockCache.return_value.get.return_value = None
            with patch("sys.stdout", new=StringIO()) as fake_out:
                search_extension("firefox", "query", csv_output=True)
                
                output = fake_out.getvalue().strip()
                reader = csv.reader(StringIO(output))
                rows = list(reader)
                
                assert rows[0] == ["id", "name", "version", "url", "description", "users", "rating"]
                assert rows[1] == ["123", "Test Ext", "1.0", "http://example.com", "Desc", "100", "4.5"]

def test_scan_csv_export(fs):
    fs.create_file("/ext.crx")
    
    mock_report = ScanReport(
        file="/ext.crx",
        libraries=[
            DetectedLibrary(
                name="jquery",
                version="1.0.0",
                path="js/jquery.js",
                vulnerable=True,
                advisory="CVE-2020-1234"
            )
        ]
    )
    
    with patch("fetchext.scanner.DependencyScanner.scan", return_value=mock_report):
        with patch("sys.stdout", new=StringIO()) as fake_out:
            scan_extension("/ext.crx", csv_output=True)
            
            output = fake_out.getvalue().strip()
            reader = csv.reader(StringIO(output))
            rows = list(reader)
            
            assert rows[0] == ["file", "library", "version", "vulnerable", "advisory", "path"]
            assert rows[1] == ["/ext.crx", "jquery", "1.0.0", "True", "CVE-2020-1234", "js/jquery.js"]
