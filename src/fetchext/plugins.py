import shutil
from pathlib import Path
from typing import List, Dict
from .config import get_config_path


class PluginManager:
    def __init__(self):
        self.hooks_dir = get_config_path().parent / "hooks"
        if not self.hooks_dir.exists():
            self.hooks_dir.mkdir(parents=True, exist_ok=True)

    def list_plugins(self) -> List[Dict[str, str]]:
        plugins = []
        for f in self.hooks_dir.iterdir():
            if f.name.endswith(".py"):
                plugins.append({"name": f.stem, "status": "enabled", "file": f.name})
            elif f.name.endswith(".py.disabled"):
                plugins.append(
                    {
                        "name": f.name.replace(".py.disabled", ""),
                        "status": "disabled",
                        "file": f.name,
                    }
                )
        return sorted(plugins, key=lambda x: x["name"])

    def enable_plugin(self, name: str) -> bool:
        disabled_path = self.hooks_dir / f"{name}.py.disabled"
        enabled_path = self.hooks_dir / f"{name}.py"

        if disabled_path.exists():
            disabled_path.rename(enabled_path)
            return True
        elif enabled_path.exists():
            return True  # Already enabled
        else:
            raise FileNotFoundError(f"Plugin '{name}' not found.")

    def disable_plugin(self, name: str) -> bool:
        enabled_path = self.hooks_dir / f"{name}.py"
        disabled_path = self.hooks_dir / f"{name}.py.disabled"

        if enabled_path.exists():
            enabled_path.rename(disabled_path)
            return True
        elif disabled_path.exists():
            return True  # Already disabled
        else:
            raise FileNotFoundError(f"Plugin '{name}' not found.")

    def install_plugin(self, source_path: Path) -> str:
        source_path = Path(source_path)
        if not source_path.exists():
            raise FileNotFoundError(f"Source file '{source_path}' not found.")

        dest_path = self.hooks_dir / source_path.name
        shutil.copy2(source_path, dest_path)
        return dest_path.stem

    def remove_plugin(self, name: str) -> bool:
        enabled_path = self.hooks_dir / f"{name}.py"
        disabled_path = self.hooks_dir / f"{name}.py.disabled"

        if enabled_path.exists():
            enabled_path.unlink()
            return True
        elif disabled_path.exists():
            disabled_path.unlink()
            return True
        else:
            raise FileNotFoundError(f"Plugin '{name}' not found.")
