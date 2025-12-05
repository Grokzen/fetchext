import os
import tomllib
from pathlib import Path
from typing import Any, Dict

def get_config_path() -> Path:
    """
    Returns the path to the configuration file.
    Respects XDG_CONFIG_HOME, defaulting to ~/.config/fext/config.toml.
    """
    xdg_config_home = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config_home:
        base_dir = Path(xdg_config_home)
    else:
        base_dir = Path.home() / ".config"
    
    return base_dir / "fext" / "config.toml"

def load_config() -> Dict[str, Any]:
    """
    Loads the configuration from the config file.
    Returns a dictionary with the configuration.
    """
    config_path = get_config_path()
    if not config_path.exists():
        return {}
    
    try:
        with open(config_path, "rb") as f:
            return tomllib.load(f)
    except Exception:
        # Log warning? For now just return empty or raise?
        # Since it's a CLI, maybe print a warning to stderr?
        # But we don't have console here easily.
        # Let's return empty and maybe log if we had logging setup.
        return {}
