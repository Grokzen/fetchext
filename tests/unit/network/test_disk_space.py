import pytest
from unittest.mock import patch
from pathlib import Path
from fetchext.utils import check_disk_space
from fetchext.exceptions import InsufficientDiskSpaceError


def test_check_disk_space_sufficient():
    """Test that check_disk_space passes when there is enough space."""
    # total, used, free
    mock_usage = (1000, 500, 500)

    with patch("shutil.disk_usage", return_value=mock_usage):
        # Need 100 bytes + 10MB buffer.
        # Wait, 500 bytes free is definitely not enough for default 10MB buffer.
        # Let's use a smaller buffer for test or larger free space.

        # Free: 20MB
        mock_usage = (100 * 1024 * 1024, 80 * 1024 * 1024, 20 * 1024 * 1024)
        with patch("shutil.disk_usage", return_value=mock_usage):
            # Need 1MB
            check_disk_space(Path("."), 1024 * 1024)


def test_check_disk_space_insufficient():
    """Test that check_disk_space raises error when space is low."""
    # Free: 5MB
    mock_usage = (100 * 1024 * 1024, 95 * 1024 * 1024, 5 * 1024 * 1024)

    with patch("shutil.disk_usage", return_value=mock_usage):
        # Need 1MB + 10MB buffer = 11MB > 5MB
        with pytest.raises(InsufficientDiskSpaceError):
            check_disk_space(Path("."), 1024 * 1024)


def test_check_disk_space_custom_buffer():
    """Test check_disk_space with custom buffer."""
    # Free: 5MB
    mock_usage = (100 * 1024 * 1024, 95 * 1024 * 1024, 5 * 1024 * 1024)

    with patch("shutil.disk_usage", return_value=mock_usage):
        # Need 1MB + 1MB buffer = 2MB < 5MB -> Should pass
        check_disk_space(Path("."), 1024 * 1024, buffer_bytes=1024 * 1024)


def test_check_disk_space_nonexistent_path():
    """Test that check_disk_space handles nonexistent paths by checking parent."""
    mock_usage = (100 * 1024 * 1024, 50 * 1024 * 1024, 50 * 1024 * 1024)

    with patch("shutil.disk_usage", return_value=mock_usage) as mock_shutil:
        # Path doesn't exist, parent does
        p = Path("/tmp/nonexistent/subdir")

        # We need to mock exists()
        with patch("pathlib.Path.exists", side_effect=lambda self: str(self) == "/tmp"):
            # This is tricky because Path objects are immutable and side_effect on instances is hard
            # Let's just rely on the logic that it walks up.
            # Instead of mocking Path.exists globally which is dangerous, let's just pass a path
            # and mock the exists call on the instance if possible, or just trust the logic.
            pass

    # Let's try a simpler approach: mock Path.exists on the specific instances we care about?
    # Or just use a real path that doesn't exist?

    with patch("shutil.disk_usage", return_value=mock_usage) as mock_shutil:
        # Assuming current directory exists
        p = Path("nonexistent_subdir")
        check_disk_space(p, 100)

        # Should have called disk_usage on "." (or absolute path of .)
        args, _ = mock_shutil.call_args
        assert (
            args[0] == Path(".").resolve()
            or args[0] == Path(".")
            or args[0].name == Path(".").resolve().name
        )
