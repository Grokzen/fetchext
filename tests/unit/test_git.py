import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from fetchext.commands.git import handle_init
from fetchext.core.constants import ExitCode


@pytest.fixture
def mock_subprocess():
    with patch("fetchext.commands.git.subprocess.run") as mock:
        yield mock


@pytest.fixture
def mock_shutil_which():
    with patch("fetchext.commands.git.shutil.which") as mock:
        mock.return_value = "/usr/bin/git"
        yield mock


def test_git_init_success(fs, mock_subprocess, mock_shutil_which):
    target_dir = Path("/tmp/extension")
    fs.create_dir(target_dir)

    args = MagicMock()
    args.directory = target_dir
    args.no_commit = False

    handle_init(args)

    # Check subprocess calls
    assert mock_subprocess.call_count == 3
    # 1. git init
    assert mock_subprocess.call_args_list[0][0][0] == ["git", "init"]
    # 2. git add .
    assert mock_subprocess.call_args_list[1][0][0] == ["git", "add", "."]
    # 3. git commit
    assert mock_subprocess.call_args_list[2][0][0] == [
        "git",
        "commit",
        "-m",
        "Initial commit (fext)",
    ]

    # Check .gitignore created
    assert (target_dir / ".gitignore").exists()
    assert "*.crx" in (target_dir / ".gitignore").read_text()


def test_git_init_no_commit(fs, mock_subprocess, mock_shutil_which):
    target_dir = Path("/tmp/extension")
    fs.create_dir(target_dir)

    args = MagicMock()
    args.directory = target_dir
    args.no_commit = True

    handle_init(args)

    assert mock_subprocess.call_count == 1
    assert mock_subprocess.call_args_list[0][0][0] == ["git", "init"]


def test_git_init_already_exists(fs, mock_subprocess, mock_shutil_which):
    target_dir = Path("/tmp/extension")
    fs.create_dir(target_dir / ".git")

    args = MagicMock()
    args.directory = target_dir

    handle_init(args)

    # Should return early
    assert mock_subprocess.call_count == 0


def test_git_not_installed(fs, mock_subprocess):
    target_dir = Path("/tmp/extension")
    fs.create_dir(target_dir)

    args = MagicMock()
    args.directory = target_dir

    with patch("fetchext.commands.git.shutil.which", return_value=None):
        with pytest.raises(SystemExit) as exc:
            handle_init(args)
        assert exc.value.code == ExitCode.DEPENDENCY


def test_git_dir_not_found(fs, mock_subprocess, mock_shutil_which):
    target_dir = Path("/tmp/nonexistent")

    args = MagicMock()
    args.directory = target_dir

    with pytest.raises(SystemExit) as exc:
        handle_init(args)
    assert exc.value.code == ExitCode.IO
