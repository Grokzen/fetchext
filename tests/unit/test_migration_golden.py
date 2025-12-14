import pytest
import json
import shutil
from pathlib import Path
from fetchext.migration import MV3Migrator

CASES_DIR = Path(__file__).parent.parent.parent / "tests/data/migration/cases"


def get_cases():
    if not CASES_DIR.exists():
        return []
    return [d.name for d in CASES_DIR.iterdir() if d.is_dir()]


@pytest.mark.parametrize("case_name", get_cases())
def test_migration_golden(case_name, tmp_path):
    """
    Golden test for MV2 -> MV3 migration.
    """
    case_dir = CASES_DIR / case_name
    input_dir = case_dir / "input"
    expected_dir = case_dir / "expected"

    # Setup: Copy input to temp dir
    work_dir = tmp_path / "extension"
    shutil.copytree(input_dir, work_dir)

    # Execute
    migrator = MV3Migrator(work_dir)
    migrator.migrate()

    # Verify Manifest
    with open(work_dir / "manifest.json") as f:
        actual_manifest = json.load(f)

    with open(expected_dir / "manifest.json") as f:
        expected_manifest = json.load(f)

    assert actual_manifest == expected_manifest, (
        f"Manifest mismatch for case '{case_name}'"
    )

    # Verify other expected files (if any)
    # For example, if expected dir has service_worker.js, check it exists and matches
    for expected_file in expected_dir.iterdir():
        if expected_file.name == "manifest.json":
            continue

        actual_file = work_dir / expected_file.name
        assert actual_file.exists(), (
            f"Expected file {expected_file.name} missing in output"
        )

        # Compare content
        assert actual_file.read_text().strip() == expected_file.read_text().strip()
