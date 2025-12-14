import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from fetchext.analysis.visual_diff import VisualDiffGenerator
from fetchext.diff import DiffReport


@pytest.fixture
def mock_diff_report():
    return DiffReport(
        old_version="1.0",
        new_version="2.0",
        added_files=["added.txt"],
        removed_files=["removed.txt"],
        modified_files=["modified.txt", "image.png"],
        image_changes=[{"file": "image.png", "diff": {"size": "10x10 -> 20x20"}}],
    )


def test_generate_visual_diff(mock_diff_report, tmp_path):
    generator = VisualDiffGenerator()
    output_path = tmp_path / "diff.html"
    old_path = Path("old.crx")
    new_path = Path("new.crx")

    with patch("fetchext.analysis.visual_diff.open_extension_archive") as mock_open:
        # Mock zip files
        mock_old_zf = MagicMock()
        mock_new_zf = MagicMock()

        # The context manager returns the mock object
        mock_old_zf.__enter__.return_value = mock_old_zf
        mock_new_zf.__enter__.return_value = mock_new_zf

        mock_open.side_effect = [mock_old_zf, mock_new_zf]

        # Mock file reads
        def read_side_effect(filename):
            if filename == "modified.txt":
                return b"old content"
            if filename == "image.png":
                return b"fake_png_bytes"
            return b""

        mock_old_zf.read.side_effect = read_side_effect

        def read_side_effect_new(filename):
            if filename == "modified.txt":
                return b"new content"
            if filename == "image.png":
                return b"fake_png_bytes_new"
            return b""

        mock_new_zf.read.side_effect = read_side_effect_new

        generator.generate(mock_diff_report, old_path, new_path, output_path)

    assert output_path.exists()
    content = output_path.read_text()

    assert "Visual Diff Report" in content
    assert "1.0" in content
    assert "2.0" in content
    assert "modified.txt" in content
    assert "image.png" in content
    # difflib might replace spaces with &nbsp;
    assert "old" in content and "content" in content
    assert "new" in content and "content" in content
    assert "data:image/png;base64" in content


def test_is_image():
    generator = VisualDiffGenerator()
    assert generator._is_image("test.png")
    assert generator._is_image("test.jpg")
    assert not generator._is_image("test.txt")


def test_is_text():
    generator = VisualDiffGenerator()
    assert generator._is_text("test.txt")
    assert generator._is_text("test.js")
    assert generator._is_text("test.json")
    assert not generator._is_text("test.png")
