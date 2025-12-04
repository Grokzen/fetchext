import logging
import requests
from pathlib import Path
from urllib.parse import urlparse
from tqdm import tqdm
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
            # Get metadata
            meta_response = requests.get(api_url)
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
            response = requests.get(download_url, stream=True)
            response.raise_for_status()

            output_path = output_dir / filename
            total_size = int(response.headers.get('content-length', 0))

            with output_path.open("wb") as f:
                if show_progress:
                    with tqdm(
                        total=total_size,
                        unit='B',
                        unit_scale=True,
                        unit_divisor=1024,
                        desc=filename,
                        leave=False
                    ) as bar:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                            bar.update(len(chunk))
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

    def search(self, query):
        url = "https://addons.mozilla.org/api/v5/addons/search/"
        params = {"q": query, "app": "firefox", "type": "extension"}

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()

            results = response.json().get("results", [])
            if results:
                print(f"Found {len(results)} results for '{query}':")
                for result in results[:5]:  # Show top 5
                    name = result.get('name', {}).get('en-US', 'Unknown Name')
                    slug = result.get('slug', 'N/A')
                    guid = result.get('guid', 'N/A')
                    url = result.get('url', 'N/A')
                    print(f"- {name}")
                    print(f"  Slug: {slug}")
                    print(f"  GUID: {guid}")
                    print(f"  URL: {url}")
                    print("")
            else:
                print(f"No results found for '{query}'.")

        except requests.RequestException as e:
            logger.error(f"Failed to search for extension: {e}")
            raise
