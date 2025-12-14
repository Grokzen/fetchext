import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from fetchext.commands.rules import handle_sync
from fetchext.constants import ExitCode


@pytest.fixture
def mock_git_installed():
    with patch("shutil.which", return_value="/usr/bin/git"):
        yield


@pytest.fixture
def mock_subprocess():
    with patch("subprocess.run") as mock:
        yield mock


def test_sync_clone_new(fs, mock_git_installed, mock_subprocess):
    """Test cloning a new repository."""
    args = MagicMock()
    args.url = "https://example.com/rules.git"
    args.dir = Path("/tmp/rules")

    handle_sync(args)

    # Verify git clone was called
    mock_subprocess.assert_called_with(
        ["git", "clone", "https://example.com/rules.git", "/tmp/rules"],
        check=True,
        capture_output=True,
    )

    # Verify parent dir created
    assert Path("/tmp").exists()


def test_sync_pull_existing(fs, mock_git_installed, mock_subprocess):
    """Test pulling an existing repository."""
    args = MagicMock()
    args.url = None
    args.dir = Path("/tmp/rules")

    # Create existing git repo structure
    fs.create_dir("/tmp/rules/.git")

    handle_sync(args)

    # Verify git pull was called
    mock_subprocess.assert_called_with(
        ["git", "pull"], cwd=Path("/tmp/rules"), check=True, capture_output=True
    )


def test_sync_existing_not_git(fs, mock_git_installed, mock_subprocess):
    """Test error when directory exists but is not a git repo."""
    args = MagicMock()
    args.url = None
    args.dir = Path("/tmp/rules")

    # Create directory without .git
    fs.create_dir("/tmp/rules")

    with pytest.raises(SystemExit) as exc:
        handle_sync(args)

    assert exc.value.code == ExitCode.IO


def test_git_not_installed(fs):
    """Test error when git is not installed."""
    args = MagicMock()
    args.url = None
    args.dir = None

    with patch("shutil.which", return_value=None):
        with pytest.raises(SystemExit) as exc:
            handle_sync(args)

    assert exc.value.code == ExitCode.DEPENDENCY
