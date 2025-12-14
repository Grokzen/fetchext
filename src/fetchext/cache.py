import json
import time
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any
from .config import load_config

logger = logging.getLogger(__name__)

class SearchCache:
    """
    Persistent cache for search results.
    """
    def __init__(self, cache_dir: Optional[Path] = None):
        if cache_dir:
            self.cache_dir = cache_dir
        else:
            # Default to ~/.cache/fext or XDG_CACHE_HOME
            # We'll use the parent of config dir for now, or standard cache location
            # get_config_path returns ~/.config/fext/config.toml usually
            # So we want ~/.cache/fext/
            import os
            xdg_cache = os.environ.get("XDG_CACHE_HOME")
            if xdg_cache:
                self.cache_dir = Path(xdg_cache) / "fext"
            else:
                self.cache_dir = Path.home() / ".cache" / "fext"
        
        self.cache_file = self.cache_dir / "search_cache.json"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self._load_config()
        self._load_cache()

    def _load_config(self):
        try:
            config = load_config()
            cache_config = config.get("cache", {})
            self.enabled = cache_config.get("enabled", True)
            self.ttl = cache_config.get("ttl", 3600) # 1 hour default
        except Exception:
            self.enabled = True
            self.ttl = 3600

    def _load_cache(self):
        self.data = {}
        if self.cache_file.exists():
            try:
                with self.cache_file.open("r") as f:
                    self.data = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load search cache: {e}")
                # Corrupt cache? Start fresh
                self.data = {}

    def _save_cache(self):
        try:
            with self.cache_file.open("w") as f:
                json.dump(self.data, f)
        except Exception as e:
            logger.warning(f"Failed to save search cache: {e}")

    def get(self, browser: str, query: str) -> Optional[List[Dict[str, Any]]]:
        if not self.enabled:
            return None
            
        key = f"{browser}:{query}"
        entry = self.data.get(key)
        
        if not entry:
            return None
            
        timestamp = entry.get("timestamp", 0)
        if time.time() - timestamp > self.ttl:
            # Expired
            del self.data[key]
            self._save_cache() # Lazy cleanup
            return None
            
        return entry.get("results")

    def set(self, browser: str, query: str, results: List[Dict[str, Any]]):
        if not self.enabled:
            return
            
        key = f"{browser}:{query}"
        self.data[key] = {
            "timestamp": time.time(),
            "results": results
        }
        self._save_cache()

    def clear(self):
        self.data = {}
        if self.cache_file.exists():
            self.cache_file.unlink()
