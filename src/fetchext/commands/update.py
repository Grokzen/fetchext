import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from ..console import console
from ..constants import ExitCode
from ..history import HistoryManager
from ..core import download_extension
from ..downloaders import get_downloader_for_browser
from ..config import load_config

logger = logging.getLogger(__name__)

def register(subparsers):
    parser = subparsers.add_parser("update", help="Update extensions")
    parser.add_argument("--all", action="store_true", help="Update all tracked extensions")
    parser.add_argument("--dry-run", action="store_true", help="Check for updates without downloading")
    parser.set_defaults(func=handle_update)

def handle_update(args, show_progress=True):
    if not args.all:
        console.print("[red]Currently only --all is supported. Use 'fext check' for single files.[/red]")
        raise SystemExit(ExitCode.USAGE)

    history = HistoryManager()
    entries = history.get_entries()
    
    # Deduplicate by ID and Browser
    unique_extensions = {}
    for entry in entries:
        # Use .get() for safe access
        action = entry.get("action")
        ext_id = entry.get("id")
        browser = entry.get("browser")
        
        if action == "download" and ext_id and browser:
            key = (browser, ext_id)
            # Keep the most recent entry for version comparison
            if key not in unique_extensions:
                unique_extensions[key] = entry
            else:
                # If current entry is newer (higher timestamp), replace
                # Assuming entries are sorted or we trust the order. 
                # HistoryManager appends, so last is newest.
                unique_extensions[key] = entry

    if not unique_extensions:
        console.print("[yellow]No download history found.[/yellow]")
        return

    console.print(f"[bold]Checking updates for {len(unique_extensions)} extensions...[/bold]")

    config = load_config()
    max_workers = config.get("network", {}).get("max_workers", 4)
    download_dir = Path(config.get("general", {}).get("download_dir", "."))

    updates_found = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_ext = {
            executor.submit(_check_update, browser, ext_id, entry.get("version")): (browser, ext_id, entry)
            for (browser, ext_id), entry in unique_extensions.items()
        }

        for future in as_completed(future_to_ext):
            browser, ext_id, entry = future_to_ext[future]
            try:
                latest_version = future.result()
                current_version = entry.get("version")
                if latest_version and latest_version != current_version:
                    updates_found.append({
                        "browser": browser,
                        "id": ext_id,
                        "old_version": current_version,
                        "new_version": latest_version,
                        "source": entry.get("source") # Note: 'source' might not be in history entry based on history.py
                    })
            except Exception as e:
                logger.warning(f"Failed to check update for {ext_id} ({browser}): {e}")

    if not updates_found:
        console.print("[green]All extensions are up to date.[/green]")
        return

    console.print(f"[bold green]Found {len(updates_found)} updates![/bold green]")
    
    if args.dry_run:
        for update in updates_found:
            console.print(f" - {update['browser']}/{update['id']}: {update['old_version']} -> {update['new_version']}")
        return

    # Perform updates
    for update in updates_found:
        console.print(f"Downloading update for [cyan]{update['id']}[/cyan] ({update['new_version']})...")
        try:
            target_url = update.get('source')
            # If source is missing or invalid, try to reconstruct
            if not target_url or "blob:" in target_url:
                 if update['browser'] == 'chrome':
                     target_url = f"https://chromewebstore.google.com/detail/{update['id']}"
                 elif update['browser'] == 'edge':
                     target_url = f"https://microsoftedge.microsoft.com/addons/detail/{update['id']}"
                 elif update['browser'] == 'firefox':
                     # For Firefox, ID in history might be slug or UUID.
                     # If it's a slug, we can use it in URL.
                     target_url = f"https://addons.mozilla.org/en-US/firefox/addon/{update['id']}/"

            download_extension(
                browser=update['browser'],
                url=target_url,
                output_dir=download_dir,
                save_metadata=True,
                show_progress=show_progress
            )
        except Exception as e:
            console.print(f"[red]Failed to update {update['id']}: {e}[/red]")

def _check_update(browser, ext_id, current_version):
    downloader_cls = get_downloader_for_browser(browser)
    if not downloader_cls:
        return None
    
    downloader = downloader_cls()
    return downloader.get_latest_version(ext_id)
