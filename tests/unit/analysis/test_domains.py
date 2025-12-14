from pathlib import Path
from fetchext.analysis.domains import extract_domains_from_text, analyze_domains
from zipfile import ZipFile


def test_extract_domains_from_text():
    text = """
    Here are some URLs:
    https://google.com
    http://example.org/path
    wss://socket.io
    ftp://files.com
    And some text.
    """
    results = extract_domains_from_text(text)

    assert "google.com" in results["domains"]
    assert "example.org" in results["domains"]
    assert "socket.io" in results["domains"]
    assert "files.com" in results["domains"]

    assert "https://google.com" in results["urls"]
    assert "http://example.org/path" in results["urls"]


def test_analyze_domains_zip(fs):
    # Create a dummy zip file
    zip_path = Path("test.zip")
    with ZipFile(zip_path, "w") as zf:
        zf.writestr("script.js", "const url = 'https://api.github.com/users';")
        zf.writestr(
            "style.css", "body { background: url('http://cdn.site.com/img.png'); }"
        )
        zf.writestr(
            "ignore.bin", b"\x00\x01\x02"
        )  # Should be ignored or handled gracefully

    results = analyze_domains(zip_path)

    assert "api.github.com" in results["domains"]
    assert "cdn.site.com" in results["domains"]
    assert "https://api.github.com/users" in results["urls"]
