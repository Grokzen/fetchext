import json
from unittest.mock import MagicMock, patch
from fetchext.workflow.diff import ExtensionDiffer


def create_mock_zip(manifest, files):
    zf = MagicMock()
    zf.read.side_effect = (
        lambda name: json.dumps(manifest).encode() if name == "manifest.json" else b""
    )

    infolist = []
    for fname, crc in files.items():
        info = MagicMock()
        info.filename = fname
        info.CRC = crc
        info.file_size = 100
        infolist.append(info)

    zf.infolist.return_value = infolist
    return zf


def test_diff_extensions():
    old_manifest = {"version": "1.0", "name": "Test"}
    new_manifest = {"version": "1.1", "name": "Test"}

    old_files = {"manifest.json": 1, "a.txt": 10, "b.txt": 20}
    new_files = {"manifest.json": 2, "a.txt": 10, "b.txt": 21, "c.txt": 30}

    old_zf = create_mock_zip(old_manifest, old_files)
    new_zf = create_mock_zip(new_manifest, new_files)

    with patch("fetchext.workflow.diff.open_extension_archive") as mock_open:
        # Mock context managers
        mock_open.side_effect = [
            MagicMock(__enter__=lambda x: old_zf, __exit__=lambda x, y, z, w: None),
            MagicMock(__enter__=lambda x: new_zf, __exit__=lambda x, y, z, w: None),
        ]

        differ = ExtensionDiffer()
        report = differ.diff("old.crx", "new.crx")

        assert report.old_version == "1.0"
        assert report.new_version == "1.1"

        assert "version" in report.manifest_changes
        assert report.manifest_changes["version"] == ("1.0", "1.1")

        assert "c.txt" in report.added_files
        assert len(report.removed_files) == 0
        assert "b.txt" in report.modified_files  # CRC changed
        assert "a.txt" not in report.modified_files  # CRC same
