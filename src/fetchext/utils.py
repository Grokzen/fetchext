import zipfile
import hashlib
from pathlib import Path
from .crx import CrxDecoder, PartialFileReader
from .exceptions import IntegrityError

def verify_file_hash(file_path: Path, expected_hash: str, algorithm: str = "sha256") -> bool:
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

def open_extension_archive(file_path):
    """
    Opens an extension file (CRX or XPI) as a ZipFile, handling CRX headers if present.
    Returns a zipfile.ZipFile object. The caller is responsible for closing it.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    # Determine offset using robust CRX parsing
    offset = CrxDecoder.get_zip_offset(path)
    
    # Open file
    f = open(path, 'rb')
    
    # Get total size to calculate slice size
    f.seek(0, 2)
    total_size = f.tell()
    
    # Create wrapper
    # Size of the slice is Total - Offset
    # We pass close_underlying=True so that when the ZipFile is closed (which closes the wrapper),
    # the underlying file handle is also closed.
    wrapper = PartialFileReader(f, offset, total_size - offset, close_underlying=True)
    
    try:
        return zipfile.ZipFile(wrapper, 'r')
    except zipfile.BadZipFile:
        wrapper.close()
        # If offset was 0, it might be a CRX that we failed to detect or a corrupted file
        # If offset was > 0, it might be a corrupted CRX
        # We can try the old fallback if we really want, but the goal is to remove hacks.
        # Let's just raise.
        raise ValueError("Not a valid ZIP or CRX file")
