# Plan: Interactive Dependency Graph

## Goal
Enhance the `fext graph` command to generate an interactive HTML visualization of the extension's internal file dependencies using D3.js (or a similar library like `vis.js` or `cytoscape.js`). This allows users to explore the structure of complex extensions dynamically.

## Objectives
1.  Update `src/fetchext/analysis/graph.py` to support HTML output.
2.  Create a template (HTML/JS) that renders a force-directed graph.
3.  Update `src/fetchext/commands/inspector.py` (or wherever `graph` command is) to add `--interactive` / `--html` flag.
4.  The output should be a standalone HTML file containing the graph data (nodes and links) embedded as JSON.

## Implementation Details

### 1. Graph Data Structure
- Reuse existing `build_dependency_graph` to get the adjacency list.
- Convert it to a node-link format:
  ```json
  {
    "nodes": [{"id": "background.js", "group": "js"}, ...],
    "links": [{"source": "background.js", "target": "utils.js"}, ...]
  }
  ```

### 2. HTML Template
- Use a CDN link for `d3.v7.min.js` or `vis-network.min.js`.
- Embed the JSON data into a `<script>` tag.
- Implement zooming, panning, and node dragging.
- Color code nodes by file type (JS, HTML, CSS, JSON).

### 3. CLI Integration
- `fext graph <file> --interactive` -> generates `<file>_graph.html` and opens it (or just saves it).

## Verification
- Generate a graph for a sample extension.
- Verify the HTML file contains the correct data.
