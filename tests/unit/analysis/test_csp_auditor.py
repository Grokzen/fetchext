import pytest
from fetchext.auditor import ExtensionAuditor, AuditReport

@pytest.fixture
def auditor():
    return ExtensionAuditor()

def test_csp_mv2_unsafe_eval(auditor):
    manifest = {
        "manifest_version": 2,
        "content_security_policy": "script-src 'self' 'unsafe-eval'; object-src 'self'"
    }
    report = AuditReport(2)
    auditor._check_csp(manifest, report)
    
    assert any("unsafe-eval" in i.message for i in report.issues)
    assert any("MV2 Policy" in i.message for i in report.issues)

def test_csp_mv2_unsafe_inline(auditor):
    manifest = {
        "manifest_version": 2,
        "content_security_policy": "script-src 'self' 'unsafe-inline'"
    }
    report = AuditReport(2)
    auditor._check_csp(manifest, report)
    
    assert any("unsafe-inline" in i.message for i in report.issues)

def test_csp_mv2_http(auditor):
    manifest = {
        "manifest_version": 2,
        "content_security_policy": "script-src 'self' http://example.com"
    }
    report = AuditReport(2)
    auditor._check_csp(manifest, report)
    
    assert any("http:" in i.message for i in report.issues)

def test_csp_mv2_wildcard(auditor):
    manifest = {
        "manifest_version": 2,
        "content_security_policy": "script-src *; object-src 'none'"
    }
    report = AuditReport(2)
    auditor._check_csp(manifest, report)
    
    assert any("wildcard" in i.message for i in report.issues)

def test_csp_mv3_extension_pages(auditor):
    manifest = {
        "manifest_version": 3,
        "content_security_policy": {
            "extension_pages": "script-src 'self' 'unsafe-eval'; object-src 'self'"
        }
    }
    report = AuditReport(3)
    auditor._check_csp(manifest, report)
    
    assert any("unsafe-eval" in i.message for i in report.issues)
    assert any("MV3 Extension Pages" in i.message for i in report.issues)

def test_csp_mv3_secure(auditor):
    manifest = {
        "manifest_version": 3,
        "content_security_policy": {
            "extension_pages": "script-src 'self'; object-src 'self'"
        }
    }
    report = AuditReport(3)
    auditor._check_csp(manifest, report)
    
    assert len(report.issues) == 0

def test_csp_missing(auditor):
    manifest = {
        "manifest_version": 3
    }
    report = AuditReport(3)
    auditor._check_csp(manifest, report)
    
    assert len(report.issues) == 0
