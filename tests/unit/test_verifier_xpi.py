import zipfile
import hashlib
import base64
import io
from fetchext.core.verifier import XpiVerifier


def test_xpi_verify_valid(fs):
    # Create a valid XPI structure
    # We construct a zip in memory and write it to the fake file
    bio = io.BytesIO()
    with zipfile.ZipFile(bio, "w") as zf:
        # Add a file
        zf.writestr("content.js", b"console.log('hello');")

        # Calculate hash
        sha256 = hashlib.sha256(b"console.log('hello');").digest()
        b64_hash = base64.b64encode(sha256).decode("utf-8")

        # Add manifest
        manifest = f"""Name: content.js
SHA256-Digest: {b64_hash}
"""
        zf.writestr("META-INF/manifest.mf", manifest)

        # Add dummy signature files
        zf.writestr("META-INF/mozilla.rsa", b"dummy_sig")
        zf.writestr("META-INF/mozilla.sf", b"dummy_sf")

    fs.create_file("test.xpi", contents=bio.getvalue())

    verifier = XpiVerifier()
    assert verifier.verify("test.xpi") is True


def test_xpi_verify_invalid_hash(fs):
    bio = io.BytesIO()
    with zipfile.ZipFile(bio, "w") as zf:
        zf.writestr("content.js", b"console.log('hacked');")

        # Hash for original content
        sha256 = hashlib.sha256(b"console.log('hello');").digest()
        b64_hash = base64.b64encode(sha256).decode("utf-8")

        manifest = f"""Name: content.js
SHA256-Digest: {b64_hash}
"""
        zf.writestr("META-INF/manifest.mf", manifest)
        zf.writestr("META-INF/mozilla.rsa", b"dummy")

    fs.create_file("test.xpi", contents=bio.getvalue())

    verifier = XpiVerifier()
    assert verifier.verify("test.xpi") is False


def test_xpi_verify_missing_sig(fs):
    bio = io.BytesIO()
    with zipfile.ZipFile(bio, "w") as zf:
        zf.writestr("content.js", b"hello")
        zf.writestr("META-INF/manifest.mf", "Name: content.js\nSHA256-Digest: ...")

    fs.create_file("test.xpi", contents=bio.getvalue())

    verifier = XpiVerifier()
    assert verifier.verify("test.xpi") is False
