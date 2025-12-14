from hypothesis import given, strategies as st, settings
import pytest
from pathlib import Path
import struct
import tempfile
from fetchext.crx import CrxDecoder


# Strategy for generating CRX components
@st.composite
def crx_components(draw):
    # Magic: mostly 'Cr24', sometimes random garbage
    magic = draw(st.one_of(st.just(b"Cr24"), st.binary(min_size=4, max_size=4)))

    # Version: mostly 3, sometimes others
    version = draw(st.one_of(st.just(3), st.integers(min_value=0, max_value=2**32 - 1)))

    # Header Data: random binary
    header_data = draw(st.binary(min_size=0, max_size=1024))

    # Header Length: mostly correct, sometimes random
    correct_len = len(header_data)
    header_len = draw(
        st.one_of(st.just(correct_len), st.integers(min_value=0, max_value=2**32 - 1))
    )

    return magic, version, header_len, header_data


@given(crx_components())
@settings(max_examples=100, deadline=None)
def test_fuzz_crx_parsing(components):
    """
    Property-based test for CrxDecoder.get_zip_offset.
    Verifies that the offset calculation is consistent with the header fields,
    regardless of whether the file is a valid CRX or not.
    """
    magic, version, header_len, header_data = components

    with tempfile.TemporaryDirectory() as tmp_dir:
        f = Path(tmp_dir) / "test.crx"

        # Construct file
        with open(f, "wb") as crx:
            crx.write(magic)
            crx.write(struct.pack("<I", version))
            crx.write(struct.pack("<I", header_len))
            crx.write(header_data)
            # Add some "zip" content
            crx.write(b"PK\x03\x04" + b"\x00" * 10)

        try:
            offset = CrxDecoder.get_zip_offset(f)

            # Verification logic
            if magic != b"Cr24":
                # Should return 0 (treated as plain zip)
                assert offset == 0
            else:
                # Valid magic
                # The current implementation calculates offset = 12 + header_len
                # It does NOT validate version or if header_len matches file size
                expected_offset = 12 + header_len
                assert offset == expected_offset

        except Exception as e:
            pytest.fail(f"CrxDecoder.get_zip_offset crashed with {components}: {e}")


@given(crx_components())
@settings(max_examples=100, deadline=None)
def test_fuzz_crx_get_id_robustness(components):
    """
    Property-based test for CrxDecoder.get_id.
    Verifies that it handles malformed headers and missing protobuf fields gracefully
    by raising ValueError or struct.error, but never crashing with other exceptions.
    """
    magic, version, header_len, header_data = components

    with tempfile.TemporaryDirectory() as tmp_dir:
        f = Path(tmp_dir) / "test.crx"

        with open(f, "wb") as crx:
            crx.write(magic)
            crx.write(struct.pack("<I", version))
            crx.write(struct.pack("<I", header_len))
            crx.write(header_data)

        try:
            CrxDecoder.get_id(f)
        except ValueError:
            # Expected for invalid CRX, missing signature, or missing public key
            pass
        except struct.error:
            # Expected for malformed protobuf parsing
            pass
        except IndexError:
            # Protobuf parsing might raise IndexError on malformed data
            pass
        except Exception as e:
            pytest.fail(f"CrxDecoder.get_id crashed with {components}: {e}")
