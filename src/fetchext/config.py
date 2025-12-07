import os
import tomllib
import tomli_w
from pathlib import Path
from typing import Any, Dict
from .exceptions import ConfigError

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
    except Exception as e:
        raise ConfigError(f"Failed to load configuration from {config_path}: {e}", original_exception=e)

def save_config(config: Dict[str, Any]) -> None:
    """
    Saves the configuration to the config file.
    """
    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, "wb") as f:
        tomli_w.dump(config, f)

def get_config_value(config: Dict[str, Any], key_path: str) -> Any:
    """
    Retrieves a value from the config using a dot-separated key path.
    Returns None if the key does not exist.
    """
    keys = key_path.split(".")
    current = config
    
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return None
            
    return current

def set_config_value(config: Dict[str, Any], key_path: str, value: Any) -> None:
    """
    Sets a value in the config using a dot-separated key path.
    Creates nested dictionaries as needed.
    """
    keys = key_path.split(".")
    current = config
    
    for i, key in enumerate(keys[:-1]):
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]
    
    current[keys[-1]] = value

