import logging
import concurrent.futures
from pathlib import Path
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from .console import console
from .downloaders import ChromeDownloader, EdgeDownloader, FirefoxDownloader

logger = logging.getLogger(__name__)

class BatchProcessor:
    def process(self, file_path, output_dir, max_workers=4):
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Batch file not found: {path}")

        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)

        with path.open('r') as f:
            lines = f.readlines()

        # Filter valid lines first
        valid_lines = [
            line.strip() for line in lines
            if line.strip() and not line.strip().startswith("#")
        ]

        logger.info(f"Processing {len(valid_lines)} items with {max_workers} workers...")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            console=console,
            transient=True
        ) as progress:
            task_id = progress.add_task("Batch Progress", total=len(valid_lines))
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all tasks
                futures = [
                    executor.submit(self._process_line, line, output_dir)
                    for line in valid_lines
                ]
                
                for future in concurrent.futures.as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        logger.error(f"Unexpected error in worker thread: {e}")
                    finally:
                        progress.advance(task_id)

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
            # Disable individual progress bars in batch mode
            downloader.download(extension_id, output_dir, show_progress=False)
        except Exception as e:
            logger.error(f"Error downloading {browser} extension '{url_or_id}': {e}")
