import pytest
import ppdeep
from pathlib import Path
from unittest.mock import MagicMock, patch
from fetchext.analysis.similarity import SimilarityEngine


@pytest.fixture
def engine():
    return SimilarityEngine()


def test_compute_hash_dir(engine, tmp_path):
    d = tmp_path / "ext"
    d.mkdir()
    (d / "a.js").write_text("var a=1;", encoding="utf-8")
    (d / "b.js").write_text("var b=2;", encoding="utf-8")

    h = engine.compute_hash(d)
    assert h != ""
    assert isinstance(h, str)


def test_compute_hash_no_js(engine, tmp_path):
    d = tmp_path / "ext"
    d.mkdir()
    (d / "a.txt").write_text("hello", encoding="utf-8")

    h = engine.compute_hash(d)
    assert h == ""


@patch("fetchext.analysis.similarity.open_extension_archive")
def test_compute_hash_archive(mock_open, engine):
    mock_zf = MagicMock()
    mock_zf.namelist.return_value = ["script.js", "style.css"]
    mock_zf.read.side_effect = [b"var x=1;"]

    mock_open.return_value.__enter__.return_value = mock_zf

    h = engine.compute_hash(Path("test.crx"))
    assert h != ""
    mock_zf.read.assert_called_with("script.js")


def test_find_similar(engine, tmp_path):
    # Create repo
    repo = tmp_path / "repo"
    repo.mkdir()

    # Create target (base)
    target = repo / "target.zip"  # Dummy extension
    # We need to mock compute_hash because we can't easily create valid zip/crx files that open_extension_archive accepts without real zip structure

    with patch.object(engine, "compute_hash") as mock_hash:
        # Setup hashes
        # ssdeep needs longer, non-repetitive content to work well
        code_base = """
        class SimilarityEngine:
            def compute_hash(self, path: Union[str, Path]) -> str:
                path = Path(path)
                content_buffer = []
                try:
                    if path.is_dir():
                        for js_file in path.rglob("*.js"):
                            try:
                                content_buffer.append(js_file.read_bytes())
                            except Exception:
                                pass
        """

        content1 = (code_base * 5).encode("utf-8")
        content2 = (
            code_base * 5 + "\n# Added a comment here to change it slightly"
        ).encode("utf-8")
        content3 = (
            b"some completely different content that has nothing to do with the above"
            * 50
        )

        h1 = ppdeep.hash(content1)
        h2 = ppdeep.hash(content2)
        h3 = ppdeep.hash(content3)

        def side_effect(p):
            resolved_p = p.resolve()
            mapping = {
                target.resolve(): h1,
                (repo / "sim.zip").resolve(): h2,
                (repo / "diff.zip").resolve(): h3,
            }
            return mapping.get(resolved_p, "")

        mock_hash.side_effect = side_effect

        # Create dummy files so glob finds them
        (repo / "sim.zip").touch()
        (repo / "diff.zip").touch()
        target.touch()  # Ensure target exists for resolve()

        matches = engine.find_similar(target, repo, threshold=50)

        assert len(matches) == 1
        assert matches[0]["file"] == str(repo / "sim.zip")
        assert matches[0]["score"] > 50
