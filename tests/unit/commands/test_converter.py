import pytest
from unittest.mock import patch
from pathlib import Path
from fetchext.core.converter import FormatConverter


@pytest.fixture
def mock_crx_decoder():
    with patch("fetchext.core.converter.CrxDecoder") as mock:
        yield mock


def test_convert_crx_to_zip(fs, mock_crx_decoder):
    # Create fake CRX
    crx_path = Path("test.crx")
    fs.create_file(crx_path, contents="HEADER_PAYLOAD")

    # Mock offset to skip "HEADER_" (7 chars)
    mock_crx_decoder.get_zip_offset.return_value = 7

    output_path = Path("test.zip")
    FormatConverter.convert_to_zip(crx_path, output_path)

    assert output_path.exists()
    assert output_path.read_text() == "PAYLOAD"


def test_convert_dir_to_zip(fs):
    # Create fake dir
    input_dir = Path("my_ext")
    fs.create_dir(input_dir)
    fs.create_file(input_dir / "manifest.json", contents="{}")

    output_path = Path("test.zip")

    # We need to mock zipfile because pyfakefs interaction with zipfile can be tricky
    # or we can trust pyfakefs handles it (it usually does).
    # Let's try real zipfile with pyfakefs.

    FormatConverter.convert_to_zip(input_dir, output_path)

    assert output_path.exists()
    # Verify zip content
    import zipfile

    with zipfile.ZipFile(output_path) as zf:
        assert "manifest.json" in zf.namelist()


def test_convert_invalid_input(fs):
    with pytest.raises(FileNotFoundError):
        FormatConverter.convert_to_zip(Path("non_existent"))
