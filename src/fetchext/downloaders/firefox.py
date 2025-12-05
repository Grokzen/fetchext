import logging
import requests
from pathlib import Path
from urllib.parse import urlparse
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, DownloadColumn, TransferSpeedColumn
from ..console import console
from ..network import get_session
from .base import BaseDownloader

logger = logging.getLogger(__name__)

class FirefoxDownloader(BaseDownloader):
    def extract_id(self, url):
        # Example: https://addons.mozilla.org/en-US/firefox/addon/ublock-origin/
        parsed_url = urlparse(url)
        path_segments = parsed_url.path.strip("/").split("/")

        # The slug is usually after 'addon'
        try:
            addon_index = path_segments.index("addon")
            if addon_index + 1 < len(path_segments):
                return path_segments[addon_index + 1]
        except ValueError:
            pass

        raise ValueError("Could not extract extension slug from Firefox Add-ons URL")

    def download(self, extension_id, output_dir, show_progress=True):
        # Use AMO API to get the download URL
        # extension_id here is the slug (e.g., 'ublock-origin')
        api_url = f"https://addons.mozilla.org/api/v5/addons/addon/{extension_id}/"

        logger.info(f"Fetching metadata for Firefox extension {extension_id}...")

        try:
            with get_session() as session:
                # Get metadata
                meta_response = session.get(api_url)
                meta_response.raise_for_status()
                data = meta_response.json()

                # Get the latest version file URL
                if "current_version" in data and "file" in data["current_version"]:
                    download_url = data["current_version"]["file"]["url"]
                    filename = Path(urlparse(download_url).path).name
                else:
                    raise RuntimeError("Could not find download URL in metadata")

                logger.info(f"Downloading from {download_url}...")

                # Download file
                response = session.get(download_url, stream=True)
                response.raise_for_status()

                output_path = output_dir / filename
            total_size = int(response.headers.get('content-length', 0))

            with output_path.open("wb") as f:
                if show_progress:
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[progress.description]{task.description}"),
                        BarColumn(),
                        TaskProgressColumn(),
                        DownloadColumn(),
                        TransferSpeedColumn(),
                        console=console,
                        transient=True
                    ) as progress:
                        task = progress.add_task(filename, total=total_size)
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                            progress.update(task, advance=len(chunk))
                else:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

            if not output_path.exists() or output_path.stat().st_size == 0:
                if output_path.exists():
                    output_path.unlink()
                raise RuntimeError("Download failed: File is empty or does not exist.")

            logger.info(f"Successfully downloaded to {output_path}")
            return output_path

        except requests.RequestException as e:
            logger.error(f"Failed to download extension: {e}")
            raise

    def get_latest_version(self, extension_id):
        api_url = f"https://addons.mozilla.org/api/v5/addons/addon/{extension_id}/"
        try:
            with get_session() as session:
                response = session.get(api_url)
                response.raise_for_status()
                data = response.json()
                if "current_version" in data:
                    return data["current_version"]["version"]
                return None
        except requests.RequestException as e:
            logger.warning(f"Failed to check version for {extension_id}: {e}")
            return None

    def search(self, query):
        url = "https://addons.mozilla.org/api/v5/addons/search/"
        params = {"q": query, "app": "firefox", "type": "extension"}

        try:
            with get_session() as session:
                response = session.get(url, params=params)
                response.raise_for_status()

                return response.json().get("results", [])

        except requests.RequestException as e:
            logger.error(f"Failed to search for extension: {e}")
            raise
