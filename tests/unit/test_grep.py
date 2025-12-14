import concurrent.futures
from unittest.mock import patch
from fetchext.analysis.grep import GrepSearcher, search_directory


def test_grep_searcher_text(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("Hello World\nFoo Bar\nHello Python", encoding="utf-8")

    searcher = GrepSearcher("Hello")
    results = searcher.search_file(f)

    assert len(results) == 2
    assert results[0]["line"] == 1
    assert results[0]["content"] == "Hello World"
    assert results[1]["line"] == 3


def test_grep_searcher_ignore_case(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("hello world", encoding="utf-8")

    searcher = GrepSearcher("HELLO", ignore_case=True)
    results = searcher.search_file(f)

    assert len(results) == 1
    assert results[0]["content"] == "hello world"


def test_search_directory(tmp_path):
    (tmp_path / "d1").mkdir()
    (tmp_path / "d1/f1.txt").write_text("match me", encoding="utf-8")
    (tmp_path / "d2").mkdir()
    (tmp_path / "d2/f2.txt").write_text("no match", encoding="utf-8")

    with patch(
        "fetchext.analysis.grep.ProcessPoolExecutor",
        concurrent.futures.ThreadPoolExecutor,
    ):
        results = search_directory(tmp_path, "match")

    assert len(results) == 2  # "match me" and "no match" both contain "match"

    with patch(
        "fetchext.analysis.grep.ProcessPoolExecutor",
        concurrent.futures.ThreadPoolExecutor,
    ):
        results = search_directory(tmp_path, "me")
    assert len(results) == 1
    assert results[0]["file"] == str(tmp_path / "d1/f1.txt")
