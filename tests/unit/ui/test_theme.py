from unittest.mock import MagicMock, patch
from fetchext.ui.theme import apply_theme, DEFAULT_THEME
from fetchext.ui.app import ExtensionApp


def test_apply_theme_default():
    """Test that apply_theme returns default CSS when no config exists."""
    app = MagicMock()
    with patch("fetchext.ui.theme.load_config", return_value={}):
        css = apply_theme(app)
        assert f"$theme-primary: {DEFAULT_THEME['primary']};" in css


def test_apply_theme_custom():
    """Test that apply_theme uses config values."""
    app = MagicMock()
    custom_config = {"tui": {"theme": {"primary": "#123456"}}}
    with patch("fetchext.ui.theme.load_config", return_value=custom_config):
        css = apply_theme(app)
        assert "$theme-primary: #123456;" in css
        assert "$primary: #123456;" in css


def test_app_on_mount_applies_theme():
    """Test that ExtensionApp.on_mount calls apply_theme and injects CSS."""
    app = ExtensionApp()
    app.stylesheet = MagicMock()

    # Mock query_one to avoid errors when looking for the table
    app.query_one = MagicMock()

    with patch("fetchext.ui.app.apply_theme", return_value="$var: red;") as mock_apply:
        app.on_mount()

        mock_apply.assert_called_once_with(app)
        app.stylesheet.add_source.assert_called_once_with("$var: red;")
