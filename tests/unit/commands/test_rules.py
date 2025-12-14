import pytest
from unittest.mock import patch, MagicMock
from fetchext.commands.rules import handle_sync, handle_list, DEFAULT_RULES_REPO, DEFAULT_RULES_DIR

@pytest.fixture
def mock_args():
    args = MagicMock()
    args.repo = None
    args.dir = None
    return args

@patch("fetchext.commands.rules.shutil.which")
@patch("fetchext.commands.rules.subprocess.run")
def test_sync_clone(mock_run, mock_which, mock_args, fs):
    mock_which.return_value = "/usr/bin/git"
    
    # Ensure directory does not exist
    if fs.exists(DEFAULT_RULES_DIR):
        import shutil
        shutil.rmtree(DEFAULT_RULES_DIR)
        
    handle_sync(mock_args)
    
    mock_run.assert_called_with(
        ["git", "clone", DEFAULT_RULES_REPO, str(DEFAULT_RULES_DIR)],
        check=True,
        stdout=None,
        stderr=None
    )

@patch("fetchext.commands.rules.shutil.which")
@patch("fetchext.commands.rules.subprocess.run")
def test_sync_pull(mock_run, mock_which, mock_args, fs):
    mock_which.return_value = "/usr/bin/git"
    
    # Create directory to simulate existing repo
    fs.create_dir(DEFAULT_RULES_DIR)
    
    handle_sync(mock_args)
    
    mock_run.assert_called_with(
        ["git", "-C", str(DEFAULT_RULES_DIR), "pull"],
        check=True,
        stdout=None,
        stderr=None
    )

@patch("fetchext.commands.rules.shutil.which")
def test_sync_no_git(mock_which, mock_args):
    mock_which.return_value = None
    
    with pytest.raises(SystemExit) as e:
        handle_sync(mock_args)
    assert e.value.code == 1

def test_list_rules(mock_args, fs, capsys):
    fs.create_dir(DEFAULT_RULES_DIR)
    fs.create_file(DEFAULT_RULES_DIR / "rule1.yar")
    fs.create_file(DEFAULT_RULES_DIR / "subdir" / "rule2.yara")
    
    handle_list(mock_args)
    
    captured = capsys.readouterr()
    assert "rule1.yar" in captured.out
    assert "subdir/rule2.yara" in captured.out
    assert "Found 2 rule files" in captured.out

def test_list_no_dir(mock_args, fs, capsys):
    # Ensure dir doesn't exist
    if fs.exists(DEFAULT_RULES_DIR):
        import shutil
        shutil.rmtree(DEFAULT_RULES_DIR)
        
    handle_list(mock_args)
    
    captured = capsys.readouterr()
    assert "does not exist" in captured.out
