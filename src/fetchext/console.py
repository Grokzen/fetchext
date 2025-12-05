from rich.console import Console
from rich.table import Table

console = Console()

def print_manifest_table(manifest):
    table = Table(title="Extension Details", show_header=True, header_style="bold magenta")
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")

    table.add_row("Name", manifest.get('name', 'N/A'))
    table.add_row("Version", manifest.get('version', 'N/A'))
    table.add_row("Manifest Version", str(manifest.get('manifest_version', 'N/A')))
    table.add_row("Description", manifest.get('description', 'N/A'))

    permissions = manifest.get('permissions', [])
    if permissions:
        table.add_row("Permissions", "\n".join(f"- {p}" for p in permissions))
    else:
        table.add_row("Permissions", "None")

    host_permissions = manifest.get('host_permissions', [])
    if host_permissions:
        table.add_row("Host Permissions", "\n".join(f"- {p}" for p in host_permissions))
    
    console.print(table)

def print_search_results_table(query, results):
    if not results:
        console.print(f"[yellow]No results found for '{query}'.[/yellow]")
        return

    table = Table(title=f"Search Results for '{query}'", show_header=True, header_style="bold magenta")
    table.add_column("Name", style="cyan")
    table.add_column("Slug", style="green")
    table.add_column("GUID", style="yellow")
    table.add_column("URL", style="blue")

    for result in results[:5]:  # Show top 5
        name_obj = result.get('name')
        if isinstance(name_obj, dict):
            name = name_obj.get('en-US', 'Unknown Name')
        else:
            name = str(name_obj) if name_obj else 'Unknown Name'
            
        slug = result.get('slug', 'N/A')
        guid = result.get('guid', 'N/A')
        url = result.get('url', 'N/A')
        table.add_row(name, slug, guid, url)
    
    console.print(table)
