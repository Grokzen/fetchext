import time
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from fetchext.interface.console  import console
from fetchext.core.core  import extract_extension, generate_report, scan_extension

logger = logging.getLogger(__name__)


class ExtensionEventHandler(FileSystemEventHandler):
    """
    Handles file system events for the directory watcher.
    """

    def __init__(self, actions=None):
        self.actions = actions or []

    def on_created(self, event):
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        if file_path.suffix.lower() in [".crx", ".xpi", ".zip"]:
            console.print_info(f"New extension detected: {file_path.name}")
            self.process_file(file_path)

    def process_file(self, file_path):
        """
        Process the new file based on configured actions.
        """
        # Wait a brief moment for file write to complete
        time.sleep(1.0)

        try:
            if "extract" in self.actions:
                console.print_info(f"Extracting {file_path.name}...")
                extract_extension(file_path, show_progress=False)

            if "report" in self.actions:
                console.print_info(f"Generating report for {file_path.name}...")
                generate_report(file_path)

            if "scan" in self.actions:
                console.print_info(f"Scanning {file_path.name}...")
                scan_extension(file_path)

            console.print_success(f"Processing complete for {file_path.name}")

        except Exception as e:
            console.print_error(f"Failed to process {file_path.name}: {e}")


class DirectoryWatcher:
    """
    Monitors a directory for new extensions.
    """

    def __init__(self, directory, actions=None):
        self.directory = Path(directory)
        self.actions = actions or []
        self.observer = Observer()

    def start(self):
        if not self.directory.exists():
            raise FileNotFoundError(f"Directory not found: {self.directory}")

        event_handler = ExtensionEventHandler(self.actions)
        self.observer.schedule(event_handler, str(self.directory), recursive=False)
        self.observer.start()

        console.print_success(f"Watching {self.directory} for new extensions...")
        console.print_info(
            f"Actions: {', '.join(self.actions) if self.actions else 'None'}"
        )
        console.print_info("Press Ctrl+C to stop.")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.observer.stop()
        self.observer.join()
        console.print_info("Watcher stopped.")
