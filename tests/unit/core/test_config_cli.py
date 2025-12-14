from unittest.mock import patch, MagicMock
from fetchext.data.config import get_config_value, set_config_value


def test_get_config_value():
    config = {
        "general": {"download_dir": "/tmp", "nested": {"key": "value"}},
        "batch": {"workers": 4},
    }

    assert get_config_value(config, "general.download_dir") == "/tmp"
    assert get_config_value(config, "batch.workers") == 4
    assert get_config_value(config, "general.nested.key") == "value"
    assert get_config_value(config, "nonexistent") is None
    assert get_config_value(config, "general.nonexistent") is None


def test_set_config_value():
    config = {}

    set_config_value(config, "general.download_dir", "/tmp")
    assert config["general"]["download_dir"] == "/tmp"

    set_config_value(config, "batch.workers", 8)
    assert config["batch"]["workers"] == 8

    set_config_value(config, "general.nested.key", "value")
    assert config["general"]["nested"]["key"] == "value"

    # Overwrite
    set_config_value(config, "batch.workers", 10)
    assert config["batch"]["workers"] == 10


@patch("fetchext.data.config.get_config_path")
@patch("builtins.open", new_callable=MagicMock)
@patch("fetchext.data.config.tomli_w.dump")
def test_save_config(mock_dump, mock_open, mock_get_path):
    from fetchext.data.config import save_config
    from pathlib import Path

    mock_path = MagicMock(spec=Path)
    mock_path.parent.mkdir.return_value = None
    mock_get_path.return_value = mock_path

    config = {"key": "value"}
    save_config(config)

    mock_path.parent.mkdir.assert_called_once_with(parents=True, exist_ok=True)
    mock_open.assert_called_once_with(mock_path, "wb")
    mock_dump.assert_called_once_with(
        config, mock_open.return_value.__enter__.return_value
    )
