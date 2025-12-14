import zipfile
from pathlib import Path
from fetchext.diff import ExtensionDiffer


def create_zip(path, files):
    with zipfile.ZipFile(path, "w") as zf:
        for name, content in files.items():
            zf.writestr(name, content)


def test_ast_diff_ignores_formatting(fs):
    if not fs.exists("/tmp"):
        fs.create_dir("/tmp")
    old_path = Path("/tmp/old.zip")
    new_path = Path("/tmp/new.zip")

    old_js = """
    function hello() {
        console.log("Hello");
    }
    """

    new_js = """function hello(){console.log("Hello");}"""

    create_zip(old_path, {"manifest.json": '{"version": "1.0"}', "script.js": old_js})

    create_zip(new_path, {"manifest.json": '{"version": "1.0"}', "script.js": new_js})

    differ = ExtensionDiffer()

    # Without AST diff, they should be different
    report = differ.diff(old_path, new_path, ast_diff=False)
    assert "script.js" in report.modified_files

    # With AST diff, they should be same
    report = differ.diff(old_path, new_path, ast_diff=True)
    assert "script.js" not in report.modified_files


def test_ast_diff_ignores_comments(fs):
    if not fs.exists("/tmp"):
        fs.create_dir("/tmp")
    old_path = Path("/tmp/old.zip")
    new_path = Path("/tmp/new.zip")

    old_js = """
    function hello() {
        // This is a comment
        console.log("Hello");
    }
    """

    new_js = """
    function hello() {
        /* Multi-line
           comment */
        console.log("Hello");
    }
    """

    create_zip(old_path, {"manifest.json": '{"version": "1.0"}', "script.js": old_js})

    create_zip(new_path, {"manifest.json": '{"version": "1.0"}', "script.js": new_js})

    differ = ExtensionDiffer()

    # Without AST diff, they should be different
    report = differ.diff(old_path, new_path, ast_diff=False)
    assert "script.js" in report.modified_files

    # With AST diff, they should be same
    report = differ.diff(old_path, new_path, ast_diff=True)
    assert "script.js" not in report.modified_files


def test_ast_diff_detects_real_changes(fs):
    if not fs.exists("/tmp"):
        fs.create_dir("/tmp")
    old_path = Path("/tmp/old.zip")
    new_path = Path("/tmp/new.zip")

    old_js = 'function hello() { console.log("Hello"); }'
    new_js = 'function hello() { console.log("World"); }'

    create_zip(old_path, {"manifest.json": '{"version": "1.0"}', "script.js": old_js})

    create_zip(new_path, {"manifest.json": '{"version": "1.0"}', "script.js": new_js})

    differ = ExtensionDiffer()

    # Should be different in both cases
    report = differ.diff(old_path, new_path, ast_diff=True)
    assert "script.js" in report.modified_files
