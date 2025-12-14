import pytest
import hashlib
from pathlib import Path
from fetchext.utils import verify_file_hash
from fetchext.exceptions import IntegrityError


def test_verify_file_hash_success(fs):
    """Test successful hash verification."""
    file_path = Path("/tmp/test.txt")
    content = b"hello world"
    fs.create_file(file_path, contents=content)

    expected_hash = hashlib.sha256(content).hexdigest()
    assert verify_file_hash(file_path, expected_hash) is True


def test_verify_file_hash_mismatch(fs):
    """Test hash verification failure."""
    file_path = Path("/tmp/test.txt")
    content = b"hello world"
    fs.create_file(file_path, contents=content)

    expected_hash = "a" * 64  # Invalid hash

    with pytest.raises(IntegrityError, match="Hash mismatch"):
        verify_file_hash(file_path, expected_hash)


def test_verify_file_hash_file_not_found(fs):
    """Test verification with missing file."""
    file_path = Path("/tmp/missing.txt")

    with pytest.raises(FileNotFoundError):
        verify_file_hash(file_path, "hash")


def test_verify_file_hash_case_insensitive(fs):
    """Test that hash verification is case insensitive."""
    file_path = Path("/tmp/test.txt")
    content = b"hello world"
    fs.create_file(file_path, contents=content)

    expected_hash = hashlib.sha256(content).hexdigest().upper()
    assert verify_file_hash(file_path, expected_hash) is True
