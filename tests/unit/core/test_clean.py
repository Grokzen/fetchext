import pytest
from pathlib import Path
from unittest.mock import patch
from fetchext.clean import clean_artifacts

@pytest.fixture
def mock_fs(fs):
    """Setup a fake filesystem with some artifacts."""
    # Create build artifacts
    fs.create_dir("build")
    fs.create_dir("dist")
    fs.create_dir("src/fetchext.egg-info")
    
    # Create pycache
    fs.create_dir("src/fetchext/__pycache__")
    fs.create_file("src/fetchext/__pycache__/foo.pyc")
    
    # Create downloads
    fs.create_dir("downloads")
    fs.create_file("downloads/ext.crx")
    
    return fs

def test_clean_dry_run(mock_fs, capsys):
    """Test that dry run lists files but deletes nothing."""
    clean_artifacts(Path("."), clean_cache=True, clean_downloads=True, download_dir=Path("downloads"), dry_run=True)
    
    assert Path("build").exists()
    assert Path("dist").exists()
    assert Path("src/fetchext/__pycache__").exists()
    assert Path("downloads/ext.crx").exists()
    
    captured = capsys.readouterr()
    assert "Found" in captured.out
    assert "items to clean" in captured.out
    assert "Dry run: No changes made" in captured.out
    assert "build" in captured.out
    assert "dist" in captured.out

def test_clean_cache_force(mock_fs):
    """Test cleaning cache artifacts with force."""
    clean_artifacts(Path("."), clean_cache=True, clean_downloads=False, force=True)
    
    assert not Path("build").exists()
    assert not Path("dist").exists()
    assert not Path("src/fetchext.egg-info").exists()
    assert not Path("src/fetchext/__pycache__").exists()
    # Downloads should remain
    assert Path("downloads/ext.crx").exists()

@patch("rich.prompt.Confirm.ask")
def test_clean_interactive_yes(mock_confirm, mock_fs):
    """Test interactive cleaning where user says yes."""
    mock_confirm.return_value = True
    
    clean_artifacts(Path("."), clean_cache=True, clean_downloads=False, force=False)
    
    assert not Path("build").exists()

@patch("rich.prompt.Confirm.ask")
def test_clean_interactive_no(mock_confirm, mock_fs):
    """Test interactive cleaning where user says no."""
    mock_confirm.return_value = False
    
    clean_artifacts(Path("."), clean_cache=True, clean_downloads=False, force=False)
    
    assert Path("build").exists()

def test_clean_downloads(mock_fs):
    """Test cleaning downloads."""
    clean_artifacts(Path("."), clean_cache=False, clean_downloads=True, download_dir=Path("downloads"), force=True)
    
    assert Path("build").exists()
    assert not Path("downloads/ext.crx").exists()
    # The directory itself might remain or be removed depending on implementation, 
    # but usually we just clean contents or the dir itself. 
    # In clean.py implementation: shutil.rmtree(download_dir)
    assert not Path("downloads").exists()
