import pytest
from unittest.mock import patch, MagicMock
from fetchext.cli import main
from fetchext.constants import ExitCode
from fetchext.exceptions import (
    NetworkError,
    ConfigError,
    SecurityError,
    InsufficientDiskSpaceError,
    NotFoundError,
)


@pytest.fixture
def mock_args():
    with patch("argparse.ArgumentParser.parse_args") as mock:
        yield mock


def test_exit_code_success(mock_args):
    mock_args.return_value = MagicMock(verbose=False, quiet=False, func=MagicMock())
    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == ExitCode.SUCCESS


def test_exit_code_network_error(mock_args):
    mock_func = MagicMock(side_effect=NetworkError("Network failed"))
    mock_args.return_value = MagicMock(verbose=False, quiet=False, func=mock_func)

    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == ExitCode.NETWORK


def test_exit_code_config_error(mock_args):
    mock_func = MagicMock(side_effect=ConfigError("Bad config"))
    mock_args.return_value = MagicMock(verbose=False, quiet=False, func=mock_func)

    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == ExitCode.CONFIG


def test_exit_code_security_error(mock_args):
    mock_func = MagicMock(side_effect=SecurityError("Security breach"))
    mock_args.return_value = MagicMock(verbose=False, quiet=False, func=mock_func)

    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == ExitCode.SECURITY


def test_exit_code_io_error(mock_args):
    mock_func = MagicMock(side_effect=InsufficientDiskSpaceError("Disk full"))
    mock_args.return_value = MagicMock(verbose=False, quiet=False, func=mock_func)

    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == ExitCode.IO


def test_exit_code_not_found_error(mock_args):
    mock_func = MagicMock(side_effect=NotFoundError("File not found"))
    mock_args.return_value = MagicMock(verbose=False, quiet=False, func=mock_func)

    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == ExitCode.NOT_FOUND


def test_exit_code_cancelled(mock_args):
    mock_func = MagicMock(side_effect=KeyboardInterrupt)
    mock_args.return_value = MagicMock(verbose=False, quiet=False, func=mock_func)

    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == ExitCode.CANCELLED


def test_exit_code_generic_error(mock_args):
    mock_func = MagicMock(side_effect=Exception("Boom"))
    mock_args.return_value = MagicMock(verbose=False, quiet=False, func=mock_func)

    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == ExitCode.ERROR
