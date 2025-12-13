# MV3 Migration Assistant

As browsers deprecate Manifest V2 (MV2), extensions must be migrated to Manifest V3 (MV3). Fetchext provides a migration assistant to automate many of the tedious changes required.

## Usage

To migrate an extension directory:

```bash
fext migrate <source_directory> [options]
```

### Arguments

-   `source_directory`: The path to the directory containing the MV2 extension.

### Options

-   `--in-place`: Modify the files directly in the source directory. (Default is to create a copy).

## What It Does

The migration tool performs the following automated tasks:

1.  **Manifest Version**: Updates `"manifest_version": 2` to `3`.
2.  **Host Permissions**: Moves host permissions (e.g., `*://*/*`) from `permissions` to `host_permissions`.
3.  **Background Scripts**:
    -   Converts `background.scripts` (array) to `background.service_worker` (string).
    -   If multiple scripts are present, creates a wrapper script (`background-wrapper.js`) that imports them all.
4.  **Browser Action**: Renames `browser_action` to `action`.
5.  **Content Security Policy**: Converts string-based `content_security_policy` to the object-based format required by MV3.
6.  **Web Accessible Resources**: Updates the structure to the new object format with `resources` and `matches`.

## Manual Steps Required

The tool handles the structural changes, but you may still need to manually update your code:
-   **DOM Access**: Service workers cannot access the DOM. You must move DOM logic to offscreen documents or content scripts.
-   **API Changes**: Some APIs (like `webRequest`) are replaced by `declarativeNetRequest`.
-   **Remote Code**: MV3 forbids remote code execution.

## Hooks

The migration process supports plugins via the `pre_migrate` and `post_migrate` hooks. See [Plugins](plugins.md) for more details.
