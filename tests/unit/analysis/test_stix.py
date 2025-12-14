import pytest
from unittest.mock import patch
from fetchext.analysis.stix import StixGenerator
from fetchext.exceptions import AnalysisError


@pytest.fixture
def mock_stix():
    with patch("fetchext.analysis.stix.STIX_AVAILABLE", True):
        # We need to patch create=True because the module might not have imported them if STIX_AVAILABLE was False initially
        with (
            patch("fetchext.analysis.stix.Bundle", create=True) as MockBundle,
            patch("fetchext.analysis.stix.File", create=True) as MockFile,
            patch("fetchext.analysis.stix.DomainName", create=True) as MockDomain,
            patch("fetchext.analysis.stix.URL", create=True) as MockURL,
            patch("fetchext.analysis.stix.Indicator", create=True) as MockIndicator,
            patch("fetchext.analysis.stix.Malware", create=True) as MockMalware,
        ):
            MockBundle.return_value.serialize.return_value = "{}"
            yield {
                "Bundle": MockBundle,
                "File": MockFile,
                "DomainName": MockDomain,
                "URL": MockURL,
                "Indicator": MockIndicator,
                "Malware": MockMalware,
            }


def test_generate_success(mock_stix, tmp_path):
    ext_path = tmp_path / "test.crx"
    generator = StixGenerator(ext_path)

    analysis_results = {
        "hash": "sha256hash",
        "domains": ["example.com"],
        "urls": ["http://example.com/api"],
        "yara_matches": {
            "script.js": [{"rule": "BadRule", "tags": ["malware"], "meta": {}}]
        },
    }

    result = generator.generate(analysis_results)

    assert result == "{}"

    # Verify objects created
    mock_stix["File"].assert_called_with(
        name="test.crx", hashes={"SHA-256": "sha256hash"}
    )
    mock_stix["DomainName"].assert_called_with(value="example.com")
    mock_stix["URL"].assert_called_with(value="http://example.com/api")
    mock_stix["Indicator"].assert_called()
    mock_stix["Malware"].assert_called()
    mock_stix["Bundle"].assert_called()


def test_generate_missing_stix(tmp_path):
    with patch("fetchext.analysis.stix.STIX_AVAILABLE", False):
        generator = StixGenerator(tmp_path / "test.crx")
        with pytest.raises(AnalysisError, match="stix2 is not installed"):
            generator.generate({})
