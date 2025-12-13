# Plan: Network Error Handling (403/429)

## Goal

Improve resilience and user feedback when encountering network errors, specifically HTTP 403 (Forbidden/Cloudflare) and HTTP 429 (Too Many Requests).

## Current State

- `download_file` uses `response.raise_for_status()`.
- `requests.RequestException` catches everything and logs a generic error.
- Users see "Failed to download file: 403 Client Error..." without context.

## Proposed Changes

### 1. Update `src/fetchext/network.py`

- In `download_file`, add a specific `except requests.HTTPError` block.
- Check `e.response.status_code`.
- **403**: Log "Access Denied. Likely WAF/Cloudflare blocking." Suggest checking VPN or IP reputation.
- **429**: Log "Rate Limit Exceeded." Suggest increasing `rate_limit_delay` in config.
- Raise `NetworkError` with these specific messages.

### 2. Update `src/fetchext/exceptions.py` (Optional)

- Could add `RateLimitError` subclass, but `NetworkError` with message is sufficient for now.

## Implementation Steps

1. Modify `src/fetchext/network.py`.
2. Add unit tests in `tests/unit/network/test_network_errors.py` (or similar) mocking 403 and 429 responses.

## Verification

- Run `pytest tests/unit/network/test_network_errors.py`.
