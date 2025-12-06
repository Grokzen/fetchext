import re
import logging
from pathlib import Path
from typing import Dict, Set
from ..utils import open_extension_archive

logger = logging.getLogger(__name__)

def build_dependency_graph(file_path: Path) -> Dict[str, Set[str]]:
    """
    Builds a dependency graph of files within the extension.
    Returns a dict where key is the file path and value is a set of imported file paths.
    """
    graph = {}
    
    # Regex for imports
    # import ... from "..."
    # import "..."
    # require("...")
    
    # Simplified regexes
    es6_import_re = re.compile(r'import\s+(?:[\w\s{},*]+\s+from\s+)?["\']([^"\']+)["\']')
    commonjs_require_re = re.compile(r'require\s*\(\s*["\']([^"\']+)["\']\s*\)')
    
    try:
        with open_extension_archive(file_path) as zf:
            # List all files to verify existence
            all_files = set(zf.namelist())
            
            for filename in all_files:
                if not filename.endswith(".js"):
                    continue
                    
                graph[filename] = set()
                
                try:
                    with zf.open(filename) as f:
                        content = f.read().decode("utf-8", errors="ignore")
                        
                    # Find imports
                    imports = es6_import_re.findall(content)
                    requires = commonjs_require_re.findall(content)
                    
                    for imp in imports + requires:
                        # Resolve path
                        resolved = _resolve_path(filename, imp)
                        
                        # Check if it exists in the archive (exact match or with .js)
                        if resolved in all_files:
                            graph[filename].add(resolved)
                        elif resolved + ".js" in all_files:
                            graph[filename].add(resolved + ".js")
                        elif resolved + "/index.js" in all_files:
                            graph[filename].add(resolved + "/index.js")
                            
                except Exception as e:
                    logger.debug(f"Error parsing {filename}: {e}")
                    
    except Exception as e:
        logger.error(f"Failed to build graph: {e}")
        raise
        
    return graph

def _resolve_path(current_file: str, import_path: str) -> str:
    """
    Resolves a relative import path.
    """
    if not import_path.startswith("."):
        return import_path # Absolute or package import
        
    current_dir = str(Path(current_file).parent)
    if current_dir == ".":
        current_dir = ""
        
    # Use pathlib to resolve
    try:
        fake_root = Path("/root")
        if current_dir:
            full_path = (fake_root / current_dir / import_path).resolve()
        else:
            full_path = (fake_root / import_path).resolve()
            
        # Check if we went above root
        if not str(full_path).startswith(str(fake_root)):
             return import_path # Invalid relative path
             
        return str(full_path.relative_to(fake_root))
    except Exception:
        return import_path

def generate_dot(graph: Dict[str, Set[str]], title: str = "Dependency Graph") -> str:
    """
    Generates a DOT string from the graph.
    """
    lines = [f'digraph "{title}" {{']
    lines.append('  rankdir=LR;')
    lines.append('  node [shape=box, style=filled, fillcolor="#e0e0e0", fontname="Helvetica"];')
    lines.append('  edge [color="#555555"];')
    
    for source, targets in graph.items():
        # Clean up names for ID
        source_id = _clean_id(source)
        lines.append(f'  "{source_id}" [label="{source}"];')
        
        for target in targets:
            target_id = _clean_id(target)
            lines.append(f'  "{source_id}" -> "{target_id}";')
            
    lines.append("}")
    return "\n".join(lines)

def _clean_id(name: str) -> str:
    return name.replace('"', '\\"')
