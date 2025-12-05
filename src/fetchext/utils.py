import zipfile
from io import BytesIO
from pathlib import Path

def open_extension_archive(file_path):
    """
    Opens an extension file (CRX or XPI) as a ZipFile, handling CRX headers if present.
    Returns a zipfile.ZipFile object. The caller is responsible for closing it.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    try:
        # Try opening as a standard zip first
        return zipfile.ZipFile(path, 'r')
    except zipfile.BadZipFile:
        # Try to find the ZIP start offset (CRX header handling)
        with open(path, 'rb') as f:
            content = f.read()
            # ZIP local file header signature is 0x04034b50
            zip_start = content.find(b'PK\x03\x04')
            if zip_start == -1:
                raise ValueError("Not a valid ZIP or CRX file")
            
            # Return a ZipFile wrapping the BytesIO of the content from offset
            return zipfile.ZipFile(BytesIO(content[zip_start:]), 'r')
