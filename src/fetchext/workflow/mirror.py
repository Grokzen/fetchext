import logging
import concurrent.futures
from pathlib import Path
from typing import List, Tuple, Set
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeRemainingColumn,
)
from fetchext.interface.console  import console
from fetchext.downloaders  import ChromeDownloader, EdgeDownloader, FirefoxDownloader
from fetchext.security.inspector  import ExtensionInspector

logger = logging.getLogger(__name__)


class MirrorManager:
    def sync(
        self,
        list_path: Path,
        output_dir: Path,
        prune: bool = False,
        workers: int = 4,
        show_progress: bool = True,
    ):
        list_path = Path(list_path)
        output_dir = Path(output_dir)

        if not list_path.exists():
            raise FileNotFoundError(f"List file not found: {list_path}")

        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)

        # Parse list
        items = self._parse_list(list_path)
        logger.info(f"Syncing {len(items)} items to {output_dir}...")

        processed_ids = set()

        if show_progress:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TimeRemainingColumn(),
                console=console,
                transient=True,
            ) as progress:
                task_id = progress.add_task("Syncing...", total=len(items))
                processed_ids = self._run_sync(
                    items, output_dir, workers, progress, task_id
                )
        else:
            processed_ids = self._run_sync(items, output_dir, workers, None, None)

        if prune:
            self._prune(output_dir, processed_ids)

    def _parse_list(self, list_path: Path) -> List[Tuple[str, str]]:
        items = []
        with list_path.open("r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split(maxsplit=1)
                if len(parts) == 2:
                    items.append((parts[0].lower(), parts[1]))
                else:
                    logger.warning(f"Invalid line: {line}")
        return items

    def _run_sync(self, items, output_dir, workers, progress, task_id) -> Set[str]:
        processed_ids = set()
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(self._sync_item, browser, url, output_dir): (
                    browser,
                    url,
                )
                for browser, url in items
            }

            for future in concurrent.futures.as_completed(futures):
                browser, url = futures[future]
                try:
                    ext_id = future.result()
                    if ext_id:
                        processed_ids.add(ext_id)
                except Exception as e:
                    logger.error(f"Error syncing {browser} {url}: {e}")
                finally:
                    if progress:
                        progress.advance(task_id)
        return processed_ids

    def _sync_item(self, browser, url, output_dir):
        downloader = self._get_downloader(browser)
        if not downloader:
            return None

        ext_id = downloader.extract_id(url)

        # Determine expected filename pattern
        # This is a heuristic. Ideally we'd know the exact filename.
        # But downloaders usually save as {id}.crx or {id}.xpi
        suffix = ".xpi" if browser in ["firefox", "f"] else ".crx"
        filename = f"{ext_id}{suffix}"
        file_path = output_dir / filename

        should_download = False

        if not file_path.exists():
            should_download = True
            logger.debug(f"{ext_id}: Missing locally.")
        else:
            # Check for update
            try:
                remote_version = downloader.get_latest_version(ext_id)
                if remote_version:
                    # Get local version
                    inspector = ExtensionInspector()
                    manifest = inspector.get_manifest(file_path)
                    local_version = manifest.get("version")

                    if local_version != remote_version:
                        should_download = True
                        logger.info(
                            f"{ext_id}: Update available ({local_version} -> {remote_version})"
                        )
                    else:
                        logger.debug(f"{ext_id}: Up to date.")
            except Exception as e:
                logger.warning(
                    f"Could not check update for {ext_id}: {e}. Skipping update check."
                )

        if should_download:
            downloader.download(ext_id, output_dir, show_progress=False)

        return ext_id

    def _get_downloader(self, browser):
        if browser in ["chrome", "c"]:
            return ChromeDownloader()
        elif browser in ["edge", "e"]:
            return EdgeDownloader()
        elif browser in ["firefox", "f"]:
            return FirefoxDownloader()
        return None

    def _prune(self, output_dir, valid_ids):
        logger.info("Pruning extraneous files...")
        count = 0
        for file_path in output_dir.iterdir():
            if file_path.suffix not in [".crx", ".xpi"]:
                continue

            file_id = file_path.stem
            if file_id not in valid_ids:
                logger.info(f"Pruning {file_path.name}")
                file_path.unlink()
                count += 1
        logger.info(f"Pruned {count} files.")
