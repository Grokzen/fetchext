import zipfile
from pathlib import Path
from ..crx import CrxDecoder, PartialFileReader

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
