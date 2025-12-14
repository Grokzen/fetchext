from fetchext.interface.theme import Theme


class LazyConsole:
    def __init__(self):
        self._console = None

    @property
    def _impl(self):
        if self._console is None:
            from rich.console import Console

            self._console = Console(theme=Theme.RICH_THEME)
        return self._console

    def __getattr__(self, name):
        return getattr(self._impl, name)

    def __enter__(self):
        return self._impl.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self._impl.__exit__(exc_type, exc_val, exc_tb)

    def create_progress(self, transient=True):
        """Creates a standard progress bar for counting items."""
        from rich.progress import (
            Progress,
            SpinnerColumn,
            TextColumn,
            BarColumn,
            TaskProgressColumn,
            TimeRemainingColumn,
        )

        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            console=self,
            transient=transient,
        )

    def create_download_progress(self, transient=True):
        """Creates a progress bar optimized for file downloads (bytes)."""
        from rich.progress import (
            Progress,
            SpinnerColumn,
            TextColumn,
            BarColumn,
            TaskProgressColumn,
            DownloadColumn,
            TransferSpeedColumn,
        )

        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            DownloadColumn(),
            TransferSpeedColumn(),
            console=self,
            transient=transient,
        )

    def print_success(self, message: str):
        self.print(Theme.format_success(message))

    def print_error(self, message: str):
        self.print(Theme.format_error(message))

    def print_warning(self, message: str):
        self.print(Theme.format_warning(message))

    def print_info(self, message: str):
        self.print(Theme.format_info(message))


console = LazyConsole()


def print_manifest_table(manifest):
    from rich.table import Table

    table = Table(
        title="Extension Details", show_header=True, header_style="bold magenta"
    )
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")

    table.add_row("Name", manifest.get("name", "N/A"))
    table.add_row("Version", manifest.get("version", "N/A"))
    table.add_row("Manifest Version", str(manifest.get("manifest_version", "N/A")))
    table.add_row("Description", manifest.get("description", "N/A"))

    permissions = manifest.get("permissions", [])
    if permissions:
        table.add_row("Permissions", "\n".join(f"- {p}" for p in permissions))
    else:
        table.add_row("Permissions", "None")

    host_permissions = manifest.get("host_permissions", [])
    if host_permissions:
        table.add_row("Host Permissions", "\n".join(f"- {p}" for p in host_permissions))

    console.print(table)


def print_search_results_table(query, results):
    from rich.table import Table

    if not results:
        console.print_warning(f"No results found for '{query}'.")
        return

    table = Table(
        title=f"Search Results for '{query}'",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("Name", style="cyan")
    table.add_column("Slug", style="green")
    table.add_column("GUID", style="yellow")
    table.add_column("URL", style="blue")

    for result in results[:5]:  # Show top 5
        name_obj = result.get("name")
        if isinstance(name_obj, dict):
            name = name_obj.get("en-US", "Unknown Name")
        else:
            name = str(name_obj) if name_obj else "Unknown Name"

        slug = result.get("slug", "N/A")
        guid = result.get("guid", "N/A")
        url = result.get("url", "N/A")
        table.add_row(name, slug, guid, url)

    console.print(table)
