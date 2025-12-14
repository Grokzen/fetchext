from unittest.mock import MagicMock, patch
from fetchext.core.packer import ExtensionPacker
from fetchext.workflow.migration import MV3Migrator


def test_packer_hooks(tmp_path):
    # Mock HookManager
    with patch("fetchext.core.packer.HookManager") as MockHookManager:
        mock_manager = MagicMock()
        MockHookManager.return_value = mock_manager

        # Setup dummy extension
        source_dir = tmp_path / "ext"
        source_dir.mkdir()
        (source_dir / "manifest.json").write_text("{}")

        packer = ExtensionPacker()
        packer.pack(source_dir, tmp_path / "out.crx")

        # Verify hooks called
        assert mock_manager.run_hook.call_count == 2
        # We can't easily check arguments with pytest.any for complex objects,
        # but we can check the hook names
        calls = [args[0] for args, _ in mock_manager.run_hook.call_args_list]
        assert "pre_pack" in calls
        assert "post_pack" in calls


def test_migrator_hooks(tmp_path):
    # Mock HookManager
    with patch("fetchext.workflow.migration.HookManager") as MockHookManager:
        mock_manager = MagicMock()
        MockHookManager.return_value = mock_manager

        # Setup dummy extension
        source_dir = tmp_path / "ext"
        source_dir.mkdir()
        (source_dir / "manifest.json").write_text('{"manifest_version": 2}')

        migrator = MV3Migrator(source_dir)
        migrator.migrate()

        # Verify hooks called
        assert mock_manager.run_hook.call_count == 2
        calls = [args[0] for args, _ in mock_manager.run_hook.call_args_list]
        assert "pre_migrate" in calls
        assert "post_migrate" in calls
