import pytest
from unittest.mock import Mock, MagicMock
from fetchext.scanner import DependencyScanner

@pytest.fixture
def mock_open_archive(mocker):
    return mocker.patch("fetchext.scanner.open_extension_archive")

def test_scan_jquery_vulnerable(tmp_path, mock_open_archive):
    # Setup
    f = tmp_path / "ext.crx"
    f.touch()
    
    # Mock ZipFile
    zf = MagicMock()
    zf.namelist.return_value = ["jquery.js"]
    
    # Mock file content
    file_mock = Mock()
    file_mock.read.return_value = b"/*! jQuery v3.4.1 */"
    zf.open.return_value.__enter__.return_value = file_mock
    
    mock_open_archive.return_value.__enter__.return_value = zf
    
    scanner = DependencyScanner()
    report = scanner.scan(f)
    
    assert len(report.libraries) == 1
    lib = report.libraries[0]
    assert lib.name == "jquery"
    assert lib.version == "3.4.1"
    assert lib.vulnerable is True

def test_scan_jquery_safe(tmp_path, mock_open_archive):
    # Setup
    f = tmp_path / "ext.crx"
    f.touch()
    
    # Mock ZipFile
    zf = MagicMock()
    zf.namelist.return_value = ["jquery.js"]
    
    # Mock file content
    file_mock = Mock()
    file_mock.read.return_value = b"/*! jQuery v3.6.0 */"
    zf.open.return_value.__enter__.return_value = file_mock
    
    mock_open_archive.return_value.__enter__.return_value = zf
    
    scanner = DependencyScanner()
    report = scanner.scan(f)
    
    assert len(report.libraries) == 1
    lib = report.libraries[0]
    assert lib.name == "jquery"
    assert lib.version == "3.6.0"
    assert lib.vulnerable is False

def test_scan_filename_detection(tmp_path, mock_open_archive):
    # Setup
    f = tmp_path / "ext.crx"
    f.touch()
    
    # Mock ZipFile
    zf = MagicMock()
    zf.namelist.return_value = ["jquery-3.4.1.min.js"]
    
    # Mock file content (no header)
    file_mock = Mock()
    file_mock.read.return_value = b"var x=1;"
    zf.open.return_value.__enter__.return_value = file_mock
    
    mock_open_archive.return_value.__enter__.return_value = zf
    
    scanner = DependencyScanner()
    report = scanner.scan(f)
    
    assert len(report.libraries) == 1
    lib = report.libraries[0]
    assert lib.name == "jquery"
    assert lib.version == "3.4.1"
    assert lib.vulnerable is True
