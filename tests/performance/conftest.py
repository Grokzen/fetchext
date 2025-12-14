import pytest
import os
import zipfile
import random
import string


@pytest.fixture(scope="session")
def large_extension_crx(tmp_path_factory):
    """
    Generates a 10MB dummy CRX file with random content.
    """
    fn = tmp_path_factory.mktemp("data") / "large.crx"

    # Create a zip file first
    zip_path = fn.with_suffix(".zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_STORED) as zf:
        # Add 100 files of 100KB each
        for i in range(100):
            content = "".join(random.choices(string.ascii_letters, k=100 * 1024))
            zf.writestr(f"file_{i}.js", content)

    # Add CRX header (mock)
    # We'll just prepend some bytes to simulate a CRX3 header
    # Real CRX3 header is complex, but for parsing speed of *our* decoder (which finds zip offset),
    # we just need a valid-looking structure or just the zip appended.
    # Our CrxDecoder looks for 'Cr24' magic.

    with open(zip_path, "rb") as f_in, open(fn, "wb") as f_out:
        # Magic
        f_out.write(b"Cr24")
        # Version 3
        f_out.write(b"\x03\x00\x00\x00")
        # Header length (mock, say 100 bytes)
        f_out.write(b"\x64\x00\x00\x00")
        # Header data (random junk)
        f_out.write(os.urandom(100))
        # Zip content
        f_out.write(f_in.read())

    return fn


@pytest.fixture(scope="session")
def large_extension_dir(tmp_path_factory):
    """
    Generates a directory with 100 files of 10KB each for analysis testing.
    """
    d = tmp_path_factory.mktemp("ext_source")
    for i in range(100):
        p = d / f"script_{i}.js"
        # Add some "code"
        content = "function foo() { return 'bar'; }\n" * 100
        p.write_text(content)
    return d
