# Welcome to fetchext

<!-- markdownlint-disable MD033 -->

**fetchext** is a powerful Python CLI tool designed to download, analyze, and audit browser extensions from Chrome, Edge, and Firefox web stores.

<div class="grid cards" markdown>

- :material-console: **[CLI Reference](cli.md)**

    Comprehensive guide to all `fext` commands, flags, and options.

- :material-microscope: **[Analysis & Forensics](analysis.md)**

    Learn how to inspect code, visualize dependencies, and detect risks.

- :material-server: **[Deployment](deployment.md)**

    Guides for Docker, local mirroring, and enterprise integration.

- :material-download: **[Installation](installation.md)**

    Get started with `pip`, `docker`, or source installation.

</div>

## Key Features

- **Multi-Browser Support**: Download from Chrome, Edge, and Firefox stores.
- **Deep Analysis**: Calculate entropy, complexity, and scan for secrets.
- **Security Auditing**: Detect MV3 issues, dangerous permissions, and vulnerable libraries.
- **Forensics**: Visualize file timelines and dependency graphs.
- **Automation**: Batch processing, JSON output, and CI/CD integration.

## Quick Start

```bash
# Install
pip install fetchext

# Download an extension
fext download chrome <url>

# Analyze it
fext analyze --risk <file>
```
