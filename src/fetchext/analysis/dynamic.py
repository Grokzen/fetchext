import asyncio
import logging
import json
import time
from pathlib import Path
from typing import Dict, List

try:
    from playwright.async_api import async_playwright, Page

    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    async_playwright = None
    Page = None

from fetchext.core.exceptions  import AnalysisError

logger = logging.getLogger(__name__)


class DynamicAnalyzer:
    def __init__(self, extension_path: Path, output_dir: Path):
        self.extension_path = extension_path
        self.output_dir = output_dir
        self.screenshots_dir = output_dir / "screenshots"
        self.logs_file = output_dir / "logs.json"
        self.network_file = output_dir / "network.json"

        self.logs: List[Dict] = []
        self.network_activity: List[Dict] = []

    async def run(self, headless: bool = True, duration: int = 10):
        if not PLAYWRIGHT_AVAILABLE:
            raise AnalysisError(
                "Playwright is not installed. Install it with 'pip install fetchext[dynamic]'"
            )

        if not self.extension_path.exists():
            raise AnalysisError(f"Extension path not found: {self.extension_path}")

        # Ensure output directories exist
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Starting dynamic analysis for {self.extension_path}")

        async with async_playwright() as p:
            # Launch browser with extension loaded
            # Note: Extensions only work in persistent contexts or with specific args
            args = [
                f"--disable-extensions-except={self.extension_path.absolute()}",
                f"--load-extension={self.extension_path.absolute()}",
            ]

            context = await p.chromium.launch_persistent_context(
                user_data_dir=self.output_dir / "user_data",
                headless=headless,
                args=args,
            )

            # Wait for extension to load (background pages, etc.)
            # We can try to find the background page or just open a new page
            page = await context.new_page()

            # Setup listeners
            self._monitor_console(page)
            self._monitor_network(page)

            # Let it run for a bit
            logger.info(f"Running for {duration} seconds...")
            await asyncio.sleep(duration)

            # Capture screenshot of whatever is visible
            await self._capture_screenshot(page, "final_state")

            # Try to find extension pages (options, popup) if possible
            # This is tricky without knowing the ID, but we can iterate targets
            for target in context.background_pages:
                logger.info(f"Found background page: {target.url}")
                await target.screenshot(path=self.screenshots_dir / "background.png")

            # Save data
            self._save_data()

            await context.close()
            logger.info("Dynamic analysis complete.")

    def _monitor_console(self, page: "Page"):
        page.on(
            "console",
            lambda msg: self.logs.append(
                {
                    "type": msg.type,
                    "text": msg.text,
                    "location": msg.location,
                    "timestamp": time.time(),
                }
            ),
        )

    def _monitor_network(self, page: "Page"):
        page.on(
            "request",
            lambda request: self.network_activity.append(
                {
                    "url": request.url,
                    "method": request.method,
                    "resource_type": request.resource_type,
                    "timestamp": time.time(),
                }
            ),
        )

    async def _capture_screenshot(self, page: "Page", name: str):
        path = self.screenshots_dir / f"{name}.png"
        await page.screenshot(path=path)
        logger.info(f"Captured screenshot: {path}")

    def _save_data(self):
        with open(self.logs_file, "w", encoding="utf-8") as f:
            json.dump(self.logs, f, indent=2)

        with open(self.network_file, "w", encoding="utf-8") as f:
            json.dump(self.network_activity, f, indent=2)
