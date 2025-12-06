from hypothesis import given, strategies as st, settings
import pytest
from pathlib import Path
import struct
import tempfile
from fetchext.crx import CrxDecoder

@given(st.binary())
@settings(max_examples=50, deadline=None)
def test_fuzz_crx_get_id(data):
    """
    Fuzz test for CrxDecoder.get_id.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        f = Path(tmp_dir) / "test.crx"
        f.write_bytes(data)
        
        try:
            CrxDecoder.get_id(f)
        except (ValueError, struct.error):
            # Expected errors for malformed data
            pass
        except Exception as e:
            pytest.fail(f"Unexpected exception: {type(e).__name__}: {e}")

@given(st.binary())
@settings(max_examples=50, deadline=None)
def test_fuzz_crx_get_zip_offset(data):
    """
    Fuzz test for CrxDecoder.get_zip_offset.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        f = Path(tmp_dir) / "test.crx"
        f.write_bytes(data)
        
        try:
            offset = CrxDecoder.get_zip_offset(f)
            assert isinstance(offset, int)
            assert offset >= 0
        except (ValueError, struct.error):
            pass
        except Exception as e:
            pytest.fail(f"Unexpected exception: {type(e).__name__}: {e}")
