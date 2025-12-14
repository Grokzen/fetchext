import pytest
from unittest.mock import patch
from fetchext.plugins.manager import PluginManager


@pytest.fixture
def mock_hooks_dir(tmp_path):
    hooks_dir = tmp_path / "hooks"
    hooks_dir.mkdir()
    return hooks_dir


@pytest.fixture
def plugin_manager(mock_hooks_dir):
    with patch("fetchext.plugins.manager.get_config_path") as mock_config:
        mock_config.return_value.parent = mock_hooks_dir.parent
        yield PluginManager()


def test_list_plugins(plugin_manager, mock_hooks_dir):
    (mock_hooks_dir / "plugin1.py").touch()
    (mock_hooks_dir / "plugin2.py.disabled").touch()

    plugins = plugin_manager.list_plugins()
    assert len(plugins) == 2
    assert plugins[0]["name"] == "plugin1"
    assert plugins[0]["status"] == "enabled"
    assert plugins[1]["name"] == "plugin2"
    assert plugins[1]["status"] == "disabled"


def test_enable_plugin(plugin_manager, mock_hooks_dir):
    (mock_hooks_dir / "plugin.py.disabled").touch()

    plugin_manager.enable_plugin("plugin")

    assert (mock_hooks_dir / "plugin.py").exists()
    assert not (mock_hooks_dir / "plugin.py.disabled").exists()


def test_disable_plugin(plugin_manager, mock_hooks_dir):
    (mock_hooks_dir / "plugin.py").touch()

    plugin_manager.disable_plugin("plugin")

    assert (mock_hooks_dir / "plugin.py.disabled").exists()
    assert not (mock_hooks_dir / "plugin.py").exists()


def test_install_plugin(plugin_manager, mock_hooks_dir, tmp_path):
    source = tmp_path / "new_plugin.py"
    source.write_text("print('hello')")

    plugin_manager.install_plugin(source)

    assert (mock_hooks_dir / "new_plugin.py").exists()
    assert (mock_hooks_dir / "new_plugin.py").read_text() == "print('hello')"


def test_remove_plugin(plugin_manager, mock_hooks_dir):
    (mock_hooks_dir / "plugin.py").touch()

    plugin_manager.remove_plugin("plugin")

    assert not (mock_hooks_dir / "plugin.py").exists()
