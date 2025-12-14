import subprocess
from unittest.mock import MagicMock, patch
from pathlib import Path
import pytest
from fetchext.commands.sandbox import DenoSandbox, handle_sandbox


@pytest.fixture
def mock_deno():
    with patch("shutil.which") as mock_which:
        mock_which.return_value = "/usr/bin/deno"
        yield mock_which


@pytest.fixture
def mock_subprocess():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = subprocess.CompletedProcess(
            args=["deno", "run"], returncode=0, stdout="Hello World", stderr=""
        )
        yield mock_run


def test_sandbox_init(mock_deno):
    sandbox = DenoSandbox()
    assert sandbox.is_available
    assert sandbox.executable == "/usr/bin/deno"


def test_sandbox_not_available():
    with patch("shutil.which") as mock_which:
        mock_which.return_value = None
        sandbox = DenoSandbox()
        assert not sandbox.is_available


def test_sandbox_run_success(mock_deno, mock_subprocess):
    sandbox = DenoSandbox()
    result = sandbox.run(Path("test.js"))

    assert result.returncode == 0
    assert result.stdout == "Hello World"

    mock_subprocess.assert_called_once()
    cmd = mock_subprocess.call_args[0][0]
    assert cmd[0] == "/usr/bin/deno"
    assert "run" in cmd
    assert "--no-prompt" in cmd
    assert str(Path("test.js")) in cmd


def test_sandbox_run_permissions(mock_deno, mock_subprocess):
    sandbox = DenoSandbox()
    sandbox.run(Path("test.js"), allow_net=True, allow_read=True)

    cmd = mock_subprocess.call_args[0][0]
    assert "--allow-net" in cmd
    assert "--allow-read" in cmd


def test_sandbox_run_timeout(mock_deno):
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.TimeoutExpired(
            cmd=["deno"], timeout=1, stderr="Timeout"
        )

        sandbox = DenoSandbox()
        result = sandbox.run(Path("test.js"), timeout=1)

        assert result.returncode == 124
        assert "Timeout" in result.stderr


def test_handle_sandbox_success(mock_deno, mock_subprocess, capsys):
    args = MagicMock()
    args.file = Path("test.js")
    args.allow_net = False
    args.allow_read = False
    args.timeout = 5
    args.args = []

    handle_sandbox(args)

    captured = capsys.readouterr()
    assert "Sandboxing test.js..." in captured.out
    assert "Output:" in captured.out
    assert "Hello World" in captured.out


def test_handle_sandbox_not_installed(capsys):
    with patch("shutil.which") as mock_which:
        mock_which.return_value = None

        args = MagicMock()
        args.file = Path("test.js")

        with pytest.raises(SystemExit) as exc:
            handle_sandbox(args)

        assert exc.value.code == 1
        captured = capsys.readouterr()
        assert "Error: Deno is not installed" in captured.out
