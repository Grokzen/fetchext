# Plugin System

`fetchext` supports a powerful plugin system that allows you to hook into various stages of the extension lifecycle. Plugins are Python scripts located in `~/.config/fext/hooks/`.

## Hook Points

The following hooks are available:

* `pre_download`: Triggered before a download starts. Can be used to validate the request or cancel the download.
* `post_download`: Triggered after a download completes successfully.
* `post_extract`: Triggered after an extension is extracted.
* `pre_analysis`: Triggered before generating a unified report. Can be used to cancel analysis.
* `post_analysis`: Triggered after a unified report is generated. Can be used to modify the report.

## Writing Plugins

Plugins are Python scripts (e.g., `my_plugin.py`) placed in the hooks directory. They should define functions matching the hook names.

### The `HookContext` Object

Each hook function receives a `context` object with the following attributes:

* `extension_id` (str): The ID of the extension.
* `browser` (str): The browser type (chrome, edge, firefox).
* `version` (Optional[str]): The version of the extension.
* `file_path` (Optional[Path]): Path to the downloaded file or extracted directory.
* `metadata` (Optional[Dict]): Metadata about the extension.
* `config` (Optional[Dict]): The full configuration dictionary.
* `args` (Optional[Any]): CLI arguments (if available).
* `cancel` (bool): Set to `True` to cancel the operation (for `pre_*` hooks).
* `result` (Any): The result of the operation (e.g., the analysis report). Can be modified in `post_*` hooks.

### Example: Cancel Download based on Config

```python
# ~/.config/fext/hooks/policy.py

def pre_download(context):
    # Check a custom config value
    allowed_browsers = context.config.get("policy", {}).get("allowed_browsers", [])
    
    if allowed_browsers and context.browser not in allowed_browsers:
        print(f"Policy Violation: Browser '{context.browser}' is not allowed.")
        context.cancel = True
```

### Example: Add Custom Field to Report

```python
# ~/.config/fext/hooks/enrich_report.py

def post_analysis(context):
    if context.result:
        context.result["custom_field"] = "Enriched by Plugin"
```

## Managing Plugins

You can manage plugins using the CLI:

```bash
# List installed plugins
fext plugin list

# Disable a plugin
fext plugin disable my_plugin

# Enable a plugin
fext plugin enable my_plugin
```
