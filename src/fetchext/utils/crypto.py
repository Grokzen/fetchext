import hashlib
from pathlib import Path
from ..exceptions import IntegrityError


def verify_file_hash(
    file_path: Path, expected_hash: str, algorithm: str = "sha256"
) -> bool:
    """
    Verifies that the file at file_path matches the expected hash.
    Raises IntegrityError if the hash does not match.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    hash_func = getattr(hashlib, algorithm, None)
    if not hash_func:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")

    hasher = hash_func()
    with open(file_path, "rb") as f:
        # Read in chunks to avoid memory issues with large files
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)

    calculated_hash = hasher.hexdigest().lower()
    expected_hash = expected_hash.lower()

    if calculated_hash != expected_hash:
        raise IntegrityError(
            f"Hash mismatch for {file_path.name}.\n"
            f"Expected ({algorithm}): {expected_hash}\n"
            f"Calculated ({algorithm}): {calculated_hash}"
        )

    return True
