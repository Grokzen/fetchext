from pathlib import Path
from fetchext.analysis.licenses import scan_licenses, _detect_license_from_text


def test_detect_license_mit():
    text = (
        "Permission is hereby granted, free of charge, to any person obtaining a copy"
    )
    assert _detect_license_from_text(text) == "MIT"


def test_detect_license_apache():
    text = "Licensed under the Apache License, Version 2.0"
    assert _detect_license_from_text(text) == "Apache-2.0"


def test_detect_license_none():
    text = "This is just some random text."
    assert _detect_license_from_text(text) is None


def test_scan_licenses_zip(fs):
    # Create a mock zip file
    import zipfile

    zip_path = Path("/tmp/test.zip")
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr(
            "LICENSE",
            "Permission is hereby granted, free of charge, to any person obtaining a copy",
        )
        zf.writestr(
            "script.js",
            "/* Licensed under the Apache License, Version 2.0 */\nconsole.log('hi');",
        )
        zf.writestr("README.md", "# Hello")

    results = scan_licenses(zip_path)

    assert "MIT" in results
    assert "LICENSE" in results["MIT"]

    assert "Apache-2.0" in results
    assert "script.js" in results["Apache-2.0"]


def test_scan_licenses_package_json(fs):
    import zipfile

    zip_path = Path("/tmp/test.zip")
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("package.json", '{"license": "MIT"}')

    results = scan_licenses(zip_path)

    assert "MIT" in results
    assert "package.json" in results["MIT"]
