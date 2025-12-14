import shutil
import re
from pathlib import Path
from ..exceptions import InsufficientDiskSpaceError

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
