# Plan: Unified Network Client

## Goal

Refactor all downloader modules to use a single, centralized `NetworkClient` class that handles rate limiting, retries, user-agent rotation, and proxying consistently.

## Current State

* `fetchext.network` provides `get_session()` and `download_file()`.
* Downloaders (`ChromeDownloader`, `EdgeDownloader`, `FirefoxDownloader`) use these but might have inconsistent usage or duplicate logic for headers/params.
* Rate limiting is currently implemented via `time.sleep` in some places or not at all.

## Steps

1. **Create `src/fetchext/client.py`**:
    * Define `NetworkClient` class.
    * Initialize with config (proxies, user-agent, rate_limit).
    * Implement `get`, `post`, `head` methods wrapping `requests.Session`.
    * Implement `download_file` method with progress bar support and resumable downloads.
    * Implement automatic rate limiting (token bucket or simple delay).
2. **Refactor `src/fetchext/downloaders/base.py`**:
    * Update `BaseDownloader` to hold a `self.client` instance of `NetworkClient`.
3. **Refactor Downloaders**:
    * Update `ChromeDownloader`, `EdgeDownloader`, `FirefoxDownloader` to use `self.client` instead of `requests` or `get_session`.
4. **Deprecate `src/fetchext/network.py`**:
    * Move useful logic to `client.py` or keep as a facade for backward compatibility.
5. **Testing**:
    * Update unit tests to mock `NetworkClient`.
    * Verify integration tests for downloads.

## Benefits

* Consistent User-Agent rotation.
* Centralized proxy configuration.
* Global rate limiting across all downloaders.
* Easier testing (mock one client).
