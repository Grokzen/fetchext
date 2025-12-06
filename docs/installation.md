# Installation

## Prerequisites

- Python 3.11 or higher

## From Source

1. Clone the repository:

   ```bash
   git clone https://github.com/grok/fetchext.git
   cd fetchext
   ```

2. Set up the environment:

   ```bash
   make setup
   ```

3. Activate the virtual environment:

   ```bash
   source .venv/bin/activate
   ```

## Development Setup

To install development dependencies (for testing, linting, and docs):

```bash
pip install -r requirements-dev.txt
```

## Docker

Pull the image from GitHub Container Registry:

```bash
docker pull ghcr.io/grok/fetchext:latest
```

Run it:

```bash
docker run --rm -v $(pwd):/data ghcr.io/grok/fetchext download chrome <url> -o /data
```
