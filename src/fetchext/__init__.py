from .cli import main
from fetchext.core.core  import (
    download_extension,
    search_extension,
    inspect_extension,
    extract_extension,
    batch_download,
    generate_report,
    convert_extension,
    get_repo_stats,
)

__all__ = [
    "main",
    "download_extension",
    "search_extension",
    "inspect_extension",
    "extract_extension",
    "batch_download",
    "generate_report",
    "convert_extension",
    "get_repo_stats",
]
