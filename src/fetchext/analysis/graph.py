import re
import logging
import json
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
    es6_import_re = re.compile(
        r'import\s+(?:[\w\s{},*]+\s+from\s+)?["\']([^"\']+)["\']'
    )
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
        return import_path  # Absolute or package import

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
            return import_path  # Invalid relative path

        return str(full_path.relative_to(fake_root)).replace("\\", "/")
    except Exception:
        return import_path


def generate_dot(graph: Dict[str, Set[str]], title: str = "Dependency Graph") -> str:
    """
    Generates a DOT string from the graph.
    """
    lines = [f'digraph "{title}" {{']
    lines.append("  rankdir=LR;")
    lines.append(
        '  node [shape=box, style=filled, fillcolor="#e0e0e0", fontname="Helvetica"];'
    )
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


def generate_html(graph: Dict[str, Set[str]], title: str = "Dependency Graph") -> str:
    """
    Generates an interactive HTML string using vis-network.
    """
    nodes = []
    edges = []
    node_ids = set()

    # Collect all nodes
    for source, targets in graph.items():
        node_ids.add(source)
        for target in targets:
            node_ids.add(target)

    # Create node objects
    for node_id in sorted(node_ids):
        # Color by extension
        color = "#97c2fc"  # Default blue
        if node_id.endswith(".js"):
            color = "#ffff00"  # Yellow
        elif node_id.endswith(".html"):
            color = "#fb7e81"  # Red
        elif node_id.endswith(".css"):
            color = "#7be141"  # Green
        elif node_id.endswith(".json"):
            color = "#6E6EFD"  # Blue

        nodes.append({"id": node_id, "label": node_id, "color": color})

    # Create edges
    for source, targets in graph.items():
        for target in targets:
            edges.append({"from": source, "to": target, "arrows": "to"})

    data = {"nodes": nodes, "edges": edges}

    json_data = json.dumps(data)

    html = f"""
<!DOCTYPE html>
<html>
<head>
  <title>{title}</title>
  <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
  <style type="text/css">
    #mynetwork {{
      width: 100%;
      height: 800px;
      border: 1px solid lightgray;
    }}
    body {{
        font-family: sans-serif;
    }}
  </style>
</head>
<body>
  <h2>{title}</h2>
  <div id="mynetwork"></div>
  <script type="text/javascript">
    var data = {json_data};
    var container = document.getElementById('mynetwork');
    var options = {{
        nodes: {{
            shape: 'box',
            font: {{
                size: 14
            }}
        }},
        physics: {{
            stabilization: false,
            barnesHut: {{
                gravitationalConstant: -8000,
                springConstant: 0.04,
                springLength: 95
            }}
        }}
    }};
    var network = new vis.Network(container, data, options);
  </script>
</body>
</html>
"""
    return html


def generate_graph(
    file_path: Path, output_path: Path = None, interactive: bool = False
):
    """
    Generates a dependency graph for the given extension file.
    """
    graph = build_dependency_graph(file_path)

    if interactive or (output_path and output_path.suffix == ".html"):
        content = generate_html(graph, title=f"Dependency Graph: {file_path.name}")
        ext = ".html"
    else:
        content = generate_dot(graph, title=f"Dependency Graph: {file_path.name}")
        ext = ".dot"

    if output_path:
        output_path.write_text(content)
        print(f"Graph saved to {output_path}")
    else:
        # Default output
        if ext == ".html":
            output_path = file_path.with_suffix(".html")
            output_path.write_text(content)
            print(f"Graph saved to {output_path}")
        else:
            print(content)
