from pathlib import Path
from fetchext.analysis.api_usage import analyze_api_usage

def test_analyze_api_usage_directory(fs):
    """Test API usage analysis on a directory."""
    fs.create_dir("/tmp/ext")
    
    js_content = """
    chrome.tabs.create({url: 'https://example.com'});
    chrome.runtime.sendMessage('hello');
    browser.storage.local.set({key: 'value'});
    """
    
    fs.create_file("/tmp/ext/background.js", contents=js_content)
    
    results = analyze_api_usage(Path("/tmp/ext"))
    
    assert results["total_calls"] == 3
    assert results["unique_apis"] == 3
    assert results["api_counts"]["chrome.tabs.create"] == 1
    assert results["api_counts"]["chrome.runtime.sendMessage"] == 1
    assert results["api_counts"]["browser.storage.local"] == 1 # Regex might capture 3 parts max?
    # Regex is: (chrome|browser)\.([a-zA-Z0-9_]+)(?:\.([a-zA-Z0-9_]+))?
    # browser.storage.local -> browser, storage, local -> browser.storage.local
    
    assert "background.js" in results["file_map"]

def test_analyze_api_usage_no_matches(fs):
    """Test analysis with no API calls."""
    fs.create_dir("/tmp/ext")
    fs.create_file("/tmp/ext/script.js", contents="console.log('hello');")
    
    results = analyze_api_usage(Path("/tmp/ext"))
    
    assert results["total_calls"] == 0
    assert results["unique_apis"] == 0
    assert not results["api_counts"]

def test_analyze_api_usage_html(fs):
    """Test API usage in HTML files."""
    fs.create_dir("/tmp/ext")
    html_content = """
    <script>
        chrome.windows.create();
    </script>
    """
    fs.create_file("/tmp/ext/popup.html", contents=html_content)
    
    results = analyze_api_usage(Path("/tmp/ext"))
    
    assert results["total_calls"] == 1
    assert results["api_counts"]["chrome.windows.create"] == 1

def test_analyze_api_usage_archive(fs):
    """Test API usage analysis on a ZIP archive."""
    import zipfile
    
    path = Path("/tmp/ext.zip")
    with zipfile.ZipFile(path, 'w') as zf:
        zf.writestr("script.js", "chrome.tabs.query({}, function() {});")
    
    results = analyze_api_usage(path)
    
    assert results["total_calls"] == 1
    assert results["api_counts"]["chrome.tabs.query"] == 1
