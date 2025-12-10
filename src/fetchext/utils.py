import zipfile
import hashlib
import shutil
import re
from pathlib import Path
from .crx import CrxDecoder, PartialFileReader
from .exceptions import IntegrityError, InsufficientDiskSpaceError

def sanitize_filename(filename: str, replacement: str = "_") -> str:
    """
    Sanitizes a filename by removing illegal characters and ensuring it's not too long.
    Safe for Windows, macOS, and Linux.
    """
    # Remove illegal characters
    # Windows: < > : " / \ | ? *
    # Linux/Mac: / (and null byte)
    # We also remove control characters
    filename = re.sub(r'[<>:"/\\|?*\x00-\x1f]', replacement, filename)
    
    # Remove leading/trailing spaces and dots (Windows issue)
    filename = filename.strip(" .")
    
    # Ensure it's not empty
    if not filename:
        filename = "unnamed_file"
        
    # Check for reserved names on Windows
    reserved_names = {
        "CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4", "COM5",
        "COM6", "COM7", "COM8", "COM9", "LPT1", "LPT2", "LPT3", "LPT4", "LPT5",
        "LPT6", "LPT7", "LPT8", "LPT9"
    }
    
    # Windows treats "CON.txt" as "CON", so we check the stem
    # But we can't easily get stem without pathlib, and we are operating on string.
    # Simple split.
    stem = filename.split('.')[0].upper()
    if stem in reserved_names:
        filename = f"{filename}{replacement}"
        
    # Truncate to 255 characters (common filesystem limit)
    # We should preserve extension if possible
    if len(filename) > 255:
        parts = filename.rsplit('.', 1)
        if len(parts) == 2:
            name, ext = parts
            ext = '.' + ext
            if len(ext) > 254: # Extension too long? Just truncate everything
                filename = filename[:255]
            else:
                filename = name[:255-len(ext)] + ext
        else:
            filename = filename[:255]
            
    return filename

def check_disk_space(path: Path, required_bytes: int, buffer_bytes: int = 10 * 1024 * 1024):
    """
    Checks if there is enough free disk space at the given path.
    Raises InsufficientDiskSpaceError if space is low.
    
    Args:
        path: The directory or file path to check.
        required_bytes: The number of bytes needed.
        buffer_bytes: Additional safety buffer (default 10MB).
    """
    # Ensure we check a directory that exists
    check_path = path if path.is_dir() else path.parent
    if not check_path.exists():
        # If parent doesn't exist, go up until we find one
        for parent in check_path.parents:
            if parent.exists():
                check_path = parent
                break
    
    total, used, free = shutil.disk_usage(check_path)
    
    if free < (required_bytes + buffer_bytes):
        raise InsufficientDiskSpaceError(
            f"Insufficient disk space on {check_path}.\n"
            f"Required: {required_bytes + buffer_bytes} bytes (including {buffer_bytes} buffer)\n"
            f"Available: {free} bytes"
        )

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
