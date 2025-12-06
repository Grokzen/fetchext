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
