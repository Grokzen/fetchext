from fetchext.secrets import SecretScanner

def test_secret_scanner_false_positives():
    scanner = SecretScanner()
    
    # Test cases
    content = """
    // Real secrets
    const apiKey = "AIzaSyD-1234567890abcdef1234567890abcde"; // Google API Key
    const awsKey = "AKIAIOSFODNN7EXAMPLE"; // AWS Key
    const genericSecret = "api_key = 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6'"; // High entropy generic
    
    // False positives
    const placeholder = "api_key = 'YOUR_API_KEY_HERE'"; // Placeholder
    const lowEntropy = "token = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaa'"; // Low entropy
    const url = "token = 'https://example.com/api/v1/resource'"; // URL
    const path = "secret = '/usr/local/bin/some/path/here'"; // Path
    const short = "key = '12345'"; // Too short (regex handles this, but good to check)
    """
    
    findings = scanner._scan_content(content, "test.js")
    
    # Extract types found
    found_types = [f.type for f in findings]
    
    assert "Google API Key" in found_types
    assert "AWS Access Key" in found_types
    assert "Generic API Key" in found_types
    
    # Check count - should be exactly 3
    assert len(findings) == 3
    
    # Verify specific matches
    generic_match = next(f for f in findings if f.type == "Generic API Key")
    # The match should be masked, so we just check it exists and corresponds to the right line
    assert generic_match.line == 5

def test_entropy_calculation():
    scanner = SecretScanner()
    
    # High entropy
    assert scanner._calculate_entropy("a1b2c3d4e5f6g7h8i9j0") > 3.0
    
    # Low entropy
    assert scanner._calculate_entropy("aaaaaaaaaaaaaaaaaaaa") < 1.0
    
    # Empty
    assert scanner._calculate_entropy("") == 0.0

def test_false_positive_list():
    scanner = SecretScanner()
    content = "api_key = 'INSERT_KEY_HERE'"
    findings = scanner._scan_content(content, "test.js")
    assert len(findings) == 0
