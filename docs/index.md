# fetchext

A Python CLI tool to download browser extensions (Chrome, Edge, Firefox) directly from their web stores.

## Features

- **Multi-Browser Support**: Download from Chrome Web Store, Microsoft Edge Add-ons, and Firefox Add-ons.
- **CRX3 Parsing**: Robust parsing of modern Chrome extension format.
- **Batch Downloading**: Download multiple extensions in parallel.
- **Analysis Tools**: Inspect manifests, scan for vulnerabilities, and generate reports.
- **Mirror Mode**: Maintain a local repository of extensions.
- **No API Keys**: Works directly with public store URLs.

## Quick Start

Install via pip (once published) or from source:

```bash
pip install fetchext
```

Download an extension:

```bash
fext chrome https://chromewebstore.google.com/detail/ublock-origin-lite/ddkjiahejlhfcafbddmgiahcphecmpfh
```
