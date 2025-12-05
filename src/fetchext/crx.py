import struct
import io
from pathlib import Path
from typing import BinaryIO

class PartialFileReader(io.IOBase):
    """
    A file-like object wrapper that exposes a slice of a file.
    It behaves like a file starting at `offset` with size `size`.
    """
    def __init__(self, file_obj: BinaryIO, offset: int, size: int, close_underlying: bool = False):
        self._file = file_obj
        self._offset = offset
        self._size = size
        self._pos = 0
        self._close_underlying = close_underlying
        # Seek to the start of the slice initially
        self._file.seek(self._offset)

    def read(self, size: int = -1) -> bytes:
        if size == -1:
            size = self._size - self._pos
        
        if self._pos + size > self._size:
            size = self._size - self._pos
        
        if size <= 0:
            return b""
        
        self._file.seek(self._offset + self._pos)
        data = self._file.read(size)
        self._pos += len(data)
        return data

    def seek(self, offset: int, whence: int = 0) -> int:
        if whence == 0:  # SEEK_SET
            self._pos = offset
        elif whence == 1:  # SEEK_CUR
            self._pos += offset
        elif whence == 2:  # SEEK_END
            self._pos = self._size + offset
        
        # Clamp position
        if self._pos < 0:
            self._pos = 0
        # We don't strictly clamp upper bound as files allow seeking past end
        
        return self._pos

    def tell(self) -> int:
        return self._pos

    def seekable(self) -> bool:
        return True

    def readable(self) -> bool:
        return True

    def close(self):
        if self._close_underlying:
            self._file.close()

class CrxDecoder:
    """
    Decodes CRX3 files to locate the embedded ZIP archive.
    """
    CRX_MAGIC = b'Cr24'
    
    @staticmethod
    def get_zip_offset(file_path: Path) -> int:
        """
        Returns the byte offset where the ZIP archive starts.
        Returns 0 if it's not a CRX file (assumes plain ZIP).
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, 'rb') as f:
            magic = f.read(4)
            if magic != CrxDecoder.CRX_MAGIC:
                return 0
            
            # Read Version (4 bytes, little-endian)
            version_bytes = f.read(4)
            if len(version_bytes) < 4:
                return 0
            version = struct.unpack('<I', version_bytes)[0]
            
            if version != 3:
                # Fallback for CRX2 or unknown, though we target CRX3
                # CRX2 has similar structure but different header fields
                # For now, if it's Cr24 but not v3, we might fail or try to parse v2
                # But let's assume v3 for modern extensions
                pass

            # Read Header Length (4 bytes, little-endian)
            header_len_bytes = f.read(4)
            if len(header_len_bytes) < 4:
                return 0
            header_len = struct.unpack('<I', header_len_bytes)[0]
            
            # Offset = Magic(4) + Version(4) + Length(4) + Header(header_len)
            return 12 + header_len
