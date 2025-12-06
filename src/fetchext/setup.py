import logging
from rich.prompt import Prompt, Confirm, IntPrompt, FloatPrompt
from .console import console
from .config import get_config_path, load_config

logger = logging.getLogger("fetchext")

def run_setup():
    """
    Run the interactive configuration wizard.
    """
    config_path = get_config_path()
    current_config = load_config()
    
    console.print("[bold]Configuration Wizard[/bold]")
    console.print(f"Config file: [blue]{config_path}[/blue]")
    
    if config_path.exists():
        if not Confirm.ask("Configuration file already exists. Do you want to overwrite it?", default=False):
            console.print("[yellow]Setup cancelled.[/yellow]")
            return

    # Defaults
    general = current_config.get("general", {})
    batch = current_config.get("batch", {})
    network = current_config.get("network", {})
    
    default_dir = general.get("download_dir", ".")
    default_metadata = general.get("save_metadata", False)
    default_extract = general.get("extract", False)
    default_workers = batch.get("workers", 4)
    default_delay = network.get("rate_limit_delay", 0.0)

    # Prompts
    console.print("\n[bold]General Settings[/bold]")
    download_dir = Prompt.ask("Default download directory", default=str(default_dir))
    save_metadata = Confirm.ask("Save metadata (JSON sidecars) by default?", default=default_metadata)
    extract = Confirm.ask("Auto-extract extensions by default?", default=default_extract)
    
    console.print("\n[bold]Batch Settings[/bold]")
    workers = IntPrompt.ask("Default number of workers for batch downloads", default=default_workers)
    
    console.print("\n[bold]Network Settings[/bold]")
    rate_limit_delay = FloatPrompt.ask("Rate limit delay (seconds between requests)", default=default_delay)

    # Generate TOML content
    toml_content = [
        "# fetchext configuration file",
        "",
        "[general]",
        f'download_dir = "{download_dir}"',
        f"save_metadata = {str(save_metadata).lower()}",
        f"extract = {str(extract).lower()}",
        "",
        "[batch]",
        f"workers = {workers}",
        "",
        "[network]",
        f"rate_limit_delay = {rate_limit_delay}",
    ]
    
    # Save
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w", encoding="utf-8") as f:
            f.write("\n".join(toml_content) + "\n")
        
        console.print(f"\n[bold green]Configuration saved to {config_path}[/bold green]")
    except Exception as e:
        logger.error(f"Failed to save configuration: {e}")
        console.print("[bold red]Error:[/bold red] Could not save configuration.")
