import pytest
from fetchext.beautify import CodeBeautifier


@pytest.fixture
def beautifier():
    return CodeBeautifier()


def test_beautify_js_string(beautifier, tmp_path):
    content = "function foo(x){return x+1;}"
    f = tmp_path / "test.js"
    f.write_text(content, encoding="utf-8")

    formatted = beautifier.beautify_file(f)
    assert "function foo(x) {" in formatted
    assert "return x + 1;" in formatted
    assert "\n" in formatted


def test_beautify_json_string(beautifier, tmp_path):
    content = '{"a":1,"b":[2,3]}'
    f = tmp_path / "test.json"
    f.write_text(content, encoding="utf-8")

    formatted = beautifier.beautify_file(f)
    assert '"a": 1' in formatted
    assert '"b": [' in formatted
    assert "\n" in formatted


def test_beautify_in_place(beautifier, tmp_path):
    content = "function foo(x){return x+1;}"
    f = tmp_path / "test.js"
    f.write_text(content, encoding="utf-8")

    beautifier.beautify_file(f, in_place=True)

    new_content = f.read_text(encoding="utf-8")
    assert "function foo(x) {" in new_content
    assert new_content != content


def test_beautify_output_file(beautifier, tmp_path):
    content = "function foo(x){return x+1;}"
    f = tmp_path / "test.js"
    f.write_text(content, encoding="utf-8")
    out = tmp_path / "out.js"

    beautifier.beautify_file(f, output_path=out)

    assert out.exists()
    new_content = out.read_text(encoding="utf-8")
    assert "function foo(x) {" in new_content


def test_beautify_directory(beautifier, tmp_path):
    d = tmp_path / "subdir"
    d.mkdir()
    (d / "a.js").write_text("var a=1;", encoding="utf-8")
    (d / "b.json").write_text('{"x":1}', encoding="utf-8")
    (d / "c.txt").write_text("ignore me", encoding="utf-8")

    beautifier.beautify_directory(d, in_place=True)

    assert "var a = 1;" in (d / "a.js").read_text(encoding="utf-8")
    assert '"x": 1' in (d / "b.json").read_text(encoding="utf-8")
    assert "ignore me" == (d / "c.txt").read_text(encoding="utf-8")
