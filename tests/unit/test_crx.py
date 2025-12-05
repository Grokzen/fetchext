import struct
import zipfile
import io
import pytest
from pathlib import Path
from fetchext.crx import CrxDecoder, PartialFileReader
from fetchext.utils import open_extension_archive

def create_mock_crx(header_content: bytes = b"header") -> bytes:
    # Create a valid ZIP
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zf:
        zf.writestr('manifest.json', '{"name": "test"}')
    zip_content = zip_buffer.getvalue()

    # Create CRX header
    magic = b'Cr24'
    version = struct.pack('<I', 3)
    header_len = struct.pack('<I', len(header_content))
    
    return magic + version + header_len + header_content + zip_content

def test_crx_decoder_offset(fs):
    crx_content = create_mock_crx(b"1234") # Header len 4
    # Offset = 4 (Magic) + 4 (Ver) + 4 (Len) + 4 (Header) = 16
    
    fs.create_file("test.crx", contents=crx_content)
    
    offset = CrxDecoder.get_zip_offset(Path("test.crx"))
    assert offset == 16

def test_crx_decoder_plain_zip(fs):
    # Plain ZIP (no CRX header)
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zf:
        zf.writestr('manifest.json', '{}')
    zip_content = zip_buffer.getvalue()
    
    fs.create_file("test.zip", contents=zip_content)
    
    offset = CrxDecoder.get_zip_offset(Path("test.zip"))
    assert offset == 0

def test_partial_file_reader(fs):
    # Create a file with "PREFIX" + "CONTENT"
    fs.create_file("test.dat", contents=b"PREFIXCONTENT")
    
    with open("test.dat", "rb") as f:
        # Wrap starting at offset 6 ("CONTENT")
        reader = PartialFileReader(f, offset=6, size=7)
        
        assert reader.read() == b"CONTENT"
        assert reader.tell() == 7
        
        reader.seek(0)
        assert reader.read(3) == b"CON"
        
        reader.seek(3)
        assert reader.read() == b"TENT"

def test_open_extension_archive_crx(fs):
    crx_content = create_mock_crx()
    fs.create_file("test.crx", contents=crx_content)
    
    with open_extension_archive("test.crx") as zf:
        assert "manifest.json" in zf.namelist()
        assert zf.read("manifest.json") == b'{"name": "test"}'

def test_open_extension_archive_zip(fs):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zf:
        zf.writestr('manifest.json', '{}')
    zip_content = zip_buffer.getvalue()
    
    fs.create_file("test.zip", contents=zip_content)
    
    with open_extension_archive("test.zip") as zf:
        assert "manifest.json" in zf.namelist()

def test_open_extension_archive_invalid(fs):
    fs.create_file("test.txt", contents=b"invalid")
    
    with pytest.raises(ValueError, match="Not a valid ZIP or CRX file"):
        open_extension_archive("test.txt")
