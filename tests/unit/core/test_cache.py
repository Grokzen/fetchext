import time
from fetchext.data.cache import SearchCache


def test_cache_init(tmp_path):
    cache = SearchCache(cache_dir=tmp_path)
    assert cache.cache_dir == tmp_path
    assert cache.cache_file == tmp_path / "search_cache.json"
    assert cache.data == {}


def test_cache_set_get(tmp_path):
    cache = SearchCache(cache_dir=tmp_path)
    results = [{"id": "abc", "name": "Test"}]

    cache.set("chrome", "test", results)

    cached = cache.get("chrome", "test")
    assert cached == results

    # Verify persistence
    cache2 = SearchCache(cache_dir=tmp_path)
    assert cache2.get("chrome", "test") == results


def test_cache_expiry(tmp_path):
    cache = SearchCache(cache_dir=tmp_path)
    cache.ttl = 0.1  # Short TTL

    results = [{"id": "abc"}]
    cache.set("chrome", "test", results)

    assert cache.get("chrome", "test") == results

    time.sleep(0.2)

    assert cache.get("chrome", "test") is None


def test_cache_disabled(tmp_path):
    cache = SearchCache(cache_dir=tmp_path)
    cache.enabled = False

    results = [{"id": "abc"}]
    cache.set("chrome", "test", results)

    assert cache.get("chrome", "test") is None
    assert cache.data == {}


def test_cache_clear(tmp_path):
    cache = SearchCache(cache_dir=tmp_path)
    cache.set("chrome", "test", [{"id": "abc"}])

    assert cache.cache_file.exists()

    cache.clear()

    assert not cache.cache_file.exists()
    assert cache.data == {}
