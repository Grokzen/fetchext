import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

class HistoryManager:
    def __init__(self):
        self.history_file = self._get_history_path()

    def _get_history_path(self) -> Path:
        """
        Returns the path to the history file.
        Respects XDG_DATA_HOME, defaulting to ~/.local/share/fext/history.json.
        """
        xdg_data_home = os.environ.get("XDG_DATA_HOME")
        if xdg_data_home:
            base_dir = Path(xdg_data_home)
        else:
            base_dir = Path.home() / ".local" / "share"
        
        return base_dir / "fext" / "history.json"

    def _load_history(self) -> List[Dict[str, Any]]:
        if not self.history_file.exists():
            return []
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return []

    def _save_history(self, history: List[Dict[str, Any]]) -> None:
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)

    def add_entry(self, 
                  action: str, 
                  extension_id: str, 
                  browser: str, 
                  version: Optional[str] = None, 
                  status: str = "success", 
                  path: Optional[str] = None) -> None:
        """
        Adds a new entry to the history log.
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "action": action,
            "id": extension_id,
            "browser": browser,
            "version": version,
            "status": status,
            "path": str(path) if path else None
        }
        
        history = self._load_history()
        history.append(entry)
        self._save_history(history)

    def get_entries(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Returns the last N history entries, most recent first.
        """
        history = self._load_history()
        # Sort by timestamp descending just in case, though append keeps order
        # Actually, append puts newest at end. So reverse it.
        return sorted(history, key=lambda x: x.get("timestamp", ""), reverse=True)[:limit]

    def clear(self) -> None:
        """
        Clears the history.
        """
        if self.history_file.exists():
            self.history_file.unlink()
