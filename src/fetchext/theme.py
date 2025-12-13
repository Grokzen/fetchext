from rich.theme import Theme as RichTheme
from rich.style import Style

class Theme:
    """Centralized theme configuration for the CLI."""

    # Status Indicators
    ICON_SUCCESS = "✅"
    ICON_ERROR = "❌"
    ICON_WARNING = "⚠️"
    ICON_INFO = "ℹ️"
    ICON_WAIT = "⏳"
    ICON_DOWNLOAD = "⬇️"
    ICON_SAVE = "💾"
    ICON_SEARCH = "🔍"
    ICON_SECURE = "🔒"
    ICON_INSECURE = "🔓"

    # Colors
    COLOR_SUCCESS = "green"
    COLOR_ERROR = "red"
    COLOR_WARNING = "yellow"
    COLOR_INFO = "blue"
    COLOR_HIGHLIGHT = "cyan"
    COLOR_MUTED = "dim"
    COLOR_PATH = "magenta"
    COLOR_ID = "bold cyan"
    COLOR_VERSION = "bold green"

    # Rich Theme
    RICH_THEME = RichTheme({
        "success": Style(color="green", bold=True),
        "error": Style(color="red", bold=True),
        "warning": Style(color="yellow", bold=True),
        "info": Style(color="blue"),
        "highlight": Style(color="cyan", bold=True),
        "muted": Style(color="white", dim=True),
        "path": Style(color="magenta"),
        "id": Style(color="cyan", bold=True),
        "version": Style(color="green", bold=True),
        "key": Style(color="cyan"),
        "value": Style(color="white"),
    })

    @classmethod
    def format_success(cls, message: str) -> str:
        return f"[{cls.COLOR_SUCCESS}]{cls.ICON_SUCCESS} {message}[/{cls.COLOR_SUCCESS}]"

    @classmethod
    def format_error(cls, message: str) -> str:
        return f"[{cls.COLOR_ERROR}]{cls.ICON_ERROR} {message}[/{cls.COLOR_ERROR}]"

    @classmethod
    def format_warning(cls, message: str) -> str:
        return f"[{cls.COLOR_WARNING}]{cls.ICON_WARNING} {message}[/{cls.COLOR_WARNING}]"

    @classmethod
    def format_info(cls, message: str) -> str:
        return f"[{cls.COLOR_INFO}]{cls.ICON_INFO} {message}[/{cls.COLOR_INFO}]"
