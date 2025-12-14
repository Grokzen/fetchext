import logging
from pathlib import Path
from typing import Dict
from datetime import datetime

try:
    from stix2 import Bundle, Indicator, Malware, File, DomainName, URL

    STIX_AVAILABLE = True
except ImportError:
    STIX_AVAILABLE = False

from fetchext.core.exceptions  import AnalysisError

logger = logging.getLogger(__name__)


class StixGenerator:
    def __init__(self, extension_path: Path):
        self.extension_path = extension_path
        self.objects = []

    def generate(self, analysis_results: Dict) -> str:
        if not STIX_AVAILABLE:
            raise AnalysisError(
                "stix2 is not installed. Install it with 'pip install fetchext[stix]'"
            )

        # Create File object for the extension
        ext_file = File(
            name=self.extension_path.name,
            hashes={"SHA-256": analysis_results.get("hash", "")},
        )
        self.objects.append(ext_file)

        # Create Observables for Domains
        domains = analysis_results.get("domains", [])
        for domain in domains:
            self.objects.append(DomainName(value=domain))

        # Create Observables for URLs
        urls = analysis_results.get("urls", [])
        for url in urls:
            self.objects.append(URL(value=url))

        # Create Indicators for YARA matches
        yara_matches = analysis_results.get("yara_matches", {})
        for filename, matches in yara_matches.items():
            for match in matches:
                indicator = Indicator(
                    name=f"YARA Match: {match['rule']}",
                    pattern=f"[file:name = '{filename}']",
                    pattern_type="stix",
                    valid_from=datetime.now(),
                )
                self.objects.append(indicator)

                # Create Malware object
                malware = Malware(name=match["rule"], is_family=False)
                self.objects.append(malware)

        # Create Bundle
        bundle = Bundle(objects=self.objects)
        return bundle.serialize(indent=2)
