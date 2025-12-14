import pytest
from unittest.mock import patch, mock_open
from fetchext.verifier import CrxVerifier

# We can't easily mock the full crypto verification without generating real keys and signatures.
# But we can test the structure parsing logic.


def test_verify_invalid_magic():
    with patch("builtins.open", mock_open(read_data=b"BADM")):
        verifier = CrxVerifier()
        with pytest.raises(ValueError, match="Not a CRX file"):
            verifier.verify("test.crx")


def test_verify_invalid_version():
    # Magic Cr24, Version 2 (unsupported)
    data = b"Cr24" + b"\x02\x00\x00\x00"
    with patch("builtins.open", mock_open(read_data=data)):
        verifier = CrxVerifier()
        with pytest.raises(ValueError, match="Unsupported CRX version"):
            verifier.verify("test.crx")


def test_verify_missing_header_fields():
    # Magic Cr24, Version 3, Header Len 0, Empty Header
    data = b"Cr24" + b"\x03\x00\x00\x00" + b"\x00\x00\x00\x00"
    with patch("builtins.open", mock_open(read_data=data)):
        verifier = CrxVerifier()
        with pytest.raises(ValueError, match="CRX Header missing signed_header_data"):
            verifier.verify("test.crx")
