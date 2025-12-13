from unittest.mock import MagicMock, patch
from fetchext.analysis.graph import build_dependency_graph, generate_dot, _resolve_path

def test_resolve_path():
    assert _resolve_path("src/main.js", "./utils.js") == "src/utils.js"
    assert _resolve_path("src/main.js", "../lib/utils.js") == "lib/utils.js"
    assert _resolve_path("main.js", "./utils.js") == "utils.js"
    assert _resolve_path("src/main.js", "lodash") == "lodash"

def test_build_dependency_graph(tmp_path):
    # Mock open_extension_archive
    with patch("fetchext.analysis.graph.open_extension_archive") as mock_open:
        mock_zip = MagicMock()
        mock_zip.namelist.return_value = ["main.js", "utils.js", "lib/helper.js"]
        
        # Mock file contents
        mock_files = {
            "main.js": 'import { foo } from "./utils.js";\nconst helper = require("./lib/helper");',
            "utils.js": 'console.log("utils");',
            "lib/helper.js": 'module.exports = {};'
        }
        
        def mock_open_file(filename):
            m = MagicMock()
            m.read.return_value = mock_files[filename].encode("utf-8")
            m.__enter__.return_value = m
            return m
            
        mock_zip.open.side_effect = mock_open_file
        mock_open.return_value.__enter__.return_value = mock_zip
        
        graph = build_dependency_graph("dummy.crx")
        
        assert "main.js" in graph
        assert "utils.js" in graph["main.js"]
        assert "lib/helper.js" in graph["main.js"] # Note: require("./lib/helper") resolves to lib/helper.js (with .js added by logic)
        
        # Check if .js was added correctly
        # In the code:
        # resolved = "lib/helper"
        # if resolved + ".js" in all_files: graph.add(resolved + ".js")
        
        assert "utils.js" in graph
        assert len(graph["utils.js"]) == 0

def test_generate_dot():
    graph = {
        "main.js": {"utils.js", "lib/helper.js"},
        "utils.js": set()
    }
    dot = generate_dot(graph, "Test Graph")
    
    assert 'digraph "Test Graph" {' in dot
    assert '"main.js" -> "utils.js";' in dot
    assert '"main.js" -> "lib/helper.js";' in dot

def test_generate_html():
    from fetchext.analysis.graph import generate_html
    graph = {
        "main.js": {"utils.js"},
        "utils.js": set()
    }
    html = generate_html(graph, "Test Graph")
    
    assert "<!DOCTYPE html>" in html
    assert "vis.Network" in html
    assert '"id": "main.js"' in html
    assert '"id": "utils.js"' in html
    assert '"from": "main.js", "to": "utils.js"' in html

def test_generate_graph_dot(capsys):
    from fetchext.analysis.graph import generate_graph
    from pathlib import Path
    with patch("fetchext.analysis.graph.build_dependency_graph") as mock_build:
        mock_build.return_value = {"main.js": {"utils.js"}}
        generate_graph(Path("dummy.crx"), None, interactive=False)
        captured = capsys.readouterr()
        assert 'digraph "Dependency Graph: dummy.crx" {' in captured.out

def test_generate_graph_html():
    from fetchext.analysis.graph import generate_graph
    from pathlib import Path
    with patch("fetchext.analysis.graph.build_dependency_graph") as mock_build:
        mock_build.return_value = {"main.js": {"utils.js"}}
        
        # Mock Path.write_text to avoid writing to disk
        with patch("pathlib.Path.write_text") as mock_write:
            generate_graph(Path("dummy.crx"), None, interactive=True)
            
            # Check that write_text was called
            assert mock_write.called
            content = mock_write.call_args[0][0]
            assert "<!DOCTYPE html>" in content
            assert "vis.Network" in content
