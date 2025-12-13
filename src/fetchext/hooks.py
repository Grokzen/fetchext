import importlib.util
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

@dataclass
class HookContext:
    """Context passed to hooks."""
    extension_id: str
    browser: str
    version: Optional[str] = None
    file_path: Optional[Path] = None
    metadata: Optional[Dict[str, Any]] = None
    config: Optional[Dict[str, Any]] = None
    args: Optional[Any] = None
    cancel: bool = False
    result: Any = None

class HookManager:
    """Manages loading and execution of plugin hooks."""

    def __init__(self, hooks_dir: Optional[Path] = None):
        self.hooks_dir = hooks_dir
        self.hooks: Dict[str, List[Callable[[HookContext], None]]] = {
            "pre_download": [],
            "post_download": [],
            "post_extract": [],
            "pre_analysis": [],
            "post_analysis": [],
            "pre_pack": [],
            "post_pack": [],
            "pre_migrate": [],
            "post_migrate": [],
        }
        if self.hooks_dir and self.hooks_dir.exists():
            self._load_hooks()

    def _load_hooks(self):
        """Load python scripts from the hooks directory."""
        logger.debug(f"Loading hooks from {self.hooks_dir}")
        for hook_file in self.hooks_dir.glob("*.py"):
            if hook_file.name.startswith("_"):
                continue
            
            try:
                self._load_module(hook_file)
            except Exception as e:
                logger.error(f"Failed to load hook {hook_file}: {e}")

    def _load_module(self, file_path: Path):
        """Import a python file as a module and register its hooks."""
        module_name = f"fetchext_hook_{file_path.stem}"
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if not spec or not spec.loader:
            return
        
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        # Register functions that match hook names
        for hook_name in self.hooks:
            if hasattr(module, hook_name):
                func = getattr(module, hook_name)
                if callable(func):
                    self.hooks[hook_name].append(func)
                    logger.debug(f"Registered {hook_name} from {file_path.name}")

    def run_hook(self, hook_name: str, context: HookContext) -> HookContext:
        """Execute all registered functions for a given hook."""
        if hook_name not in self.hooks:
            return context

        for func in self.hooks[hook_name]:
            try:
                func(context)
                if context.cancel:
                    logger.info(f"Hook {hook_name} requested cancellation.")
                    break
            except Exception as e:
                logger.error(f"Error in hook {hook_name}: {e}")
        
        return context
