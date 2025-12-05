import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from .downloaders import ChromeDownloader, EdgeDownloader, FirefoxDownloader
from .inspector import ExtensionInspector
from .batch import BatchProcessor
from .utils import open_extension_archive
from .console import console, print_manifest_table, print_search_results_table

logger = logging.getLogger("fetchext")

def get_downloader(browser):
    """Factory to get the appropriate downloader instance."""
    if browser in ["chrome", "c"]:
        return ChromeDownloader()
    elif browser in ["edge", "e"]:
        return EdgeDownloader()
    elif browser in ["firefox", "f"]:
        return FirefoxDownloader()
    return None

def download_extension(browser, url, output_dir, save_metadata=False, extract=False, show_progress=True):
    """
    Download an extension from a web store.
    """
    downloader = get_downloader(browser)
    if not downloader:
        raise ValueError(f"Unsupported browser type: {browser}")

    extension_id = downloader.extract_id(url)
    if show_progress:
        logger.info(f"Extracted ID/Slug: {extension_id}")

    output_dir = Path(output_dir)
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    output_path = downloader.download(extension_id, output_dir, show_progress=show_progress)
    
    if save_metadata:
        if show_progress:
            logger.info("Generating metadata sidecar...")
        try:
            inspector = ExtensionInspector()
            manifest = inspector.get_manifest(output_path)
            
            metadata = {
                "id": extension_id,
                "name": manifest.get("name", "Unknown"),
                "version": manifest.get("version", "Unknown"),
                "source_url": url,
                "download_timestamp": datetime.now(timezone.utc).isoformat(),
                "filename": output_path.name
            }
            
            # Save as <filename>.json (e.g. extension.crx.json)
            metadata_path = output_path.with_suffix(output_path.suffix + ".json")
            
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)
                
            if show_progress:
                logger.info(f"Metadata saved to {metadata_path}")
        except Exception as e:
            logger.warning(f"Failed to generate metadata: {e}")

    if extract:
        extract_extension(output_path, output_dir / output_path.stem, show_progress=show_progress)

    return output_path

def search_extension(browser, query, json_output=False):
    """
    Search for an extension.
    """
    downloader = get_downloader(browser)
    if not downloader:
        raise ValueError(f"Unsupported browser type: {browser}")
        
    if not hasattr(downloader, 'search'):
         raise ValueError(f"Search not supported for {browser}")
    
    results = downloader.search(query)
    
    if json_output:
        console.print_json(data=results)
    else:
        print_search_results_table(query, results)
    
    return results

def inspect_extension(file_path, show_progress=True, json_output=False):
    """
    Inspect an extension file.
    """
    inspector = ExtensionInspector()
    manifest = inspector.get_manifest(file_path)
    
    if json_output:
        console.print_json(data=manifest)
    else:
        print_manifest_table(manifest)
        if show_progress:
            logger.info("Inspection finished successfully.")
    
    return manifest

def extract_extension(file_path, output_dir=None, show_progress=True):
    """
    Extract an extension archive.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if output_dir:
        extract_dir = Path(output_dir)
    else:
        extract_dir = Path(".") / file_path.stem
        
    if extract_dir.exists() and any(extract_dir.iterdir()):
         logger.warning(f"Extraction directory {extract_dir} is not empty.")
    
    extract_dir.mkdir(parents=True, exist_ok=True)
    
    if show_progress:
        logger.info(f"Extracting {file_path} to {extract_dir}...")
    
    try:
        with open_extension_archive(file_path) as zf:
            zf.extractall(extract_dir)
        if show_progress:
            logger.info(f"Successfully extracted to {extract_dir}")
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        raise

def batch_download(file_path, output_dir, workers=4, show_progress=True):
    """
    Process a batch file of extension URLs.
    """
    processor = BatchProcessor()
    processor.process(file_path, output_dir, max_workers=workers, show_progress=show_progress)
    if show_progress:
        logger.info("Batch processing finished successfully.")
