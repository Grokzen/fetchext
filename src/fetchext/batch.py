import logging
from pathlib import Path
from .downloaders import ChromeDownloader, EdgeDownloader, FirefoxDownloader

logger = logging.getLogger(__name__)

class BatchProcessor:
    def process(self, file_path, output_dir):
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Batch file not found: {path}")

        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)

        with path.open('r') as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            try:
                self._process_line(line, output_dir)
            except Exception as e:
                logger.error(f"Failed to process line '{line}': {e}")

    def _process_line(self, line, output_dir):
        # Format: <browser> <url_or_id>
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            logger.warning(f"Invalid line format: '{line}'. Expected '<browser> <url_or_id>'")
            return

        browser, url_or_id = parts
        browser = browser.lower()

        downloader = None
        if browser in ["chrome", "c"]:
            downloader = ChromeDownloader()
        elif browser in ["edge", "e"]:
            downloader = EdgeDownloader()
        elif browser in ["firefox", "f"]:
            downloader = FirefoxDownloader()
        else:
            logger.warning(f"Unsupported browser in batch file: '{browser}'")
            return

        try:
            extension_id = downloader.extract_id(url_or_id)
            logger.info(f"Batch: Downloading {browser} extension {extension_id}...")
            downloader.download(extension_id, output_dir)
        except Exception as e:
            logger.error(f"Error downloading {browser} extension '{url_or_id}': {e}")
