# Configuration

`fetchext` supports a configuration file at `~/.config/fext/config.toml` (or `$XDG_CONFIG_HOME/fext/config.toml`).

## Setup

Run `fext setup` to generate a default configuration file interactively.

## Configuration File

The configuration file is in TOML format. Below are the supported sections and keys.

```toml
[general]
# Directory to save downloaded extensions
download_dir = "downloads"

# Automatically save metadata JSON sidecar files
save_metadata = false

# Custom User-Agent string for network requests
user_agent = "Mozilla/5.0 ..."

[batch]
# Number of concurrent workers for batch downloads
workers = 4

# Delay (in seconds) between requests to avoid rate limiting
delay = 0.0

[network]
# Request timeout in seconds
timeout = 30

# Number of retries for failed requests
retries = 3

# Proxy Configuration
[network.proxies]
http = "http://10.10.1.10:3128"
https = "http://10.10.1.10:1080"

[sharing]
# Sharing provider (currently only "gist" is supported)
provider = "gist"

# GitHub Personal Access Token for Gist uploads
github_token = "ghp_..."

# Whether to create public Gists (default: false)
public = false
```

## Environment Variables

You can also override configuration using environment variables, though the config file is preferred.

* `XDG_CONFIG_HOME`: Custom location for the configuration directory.
