import re
import json
from pathlib import Path
from typing import List, Dict
from zipfile import ZipFile
from fetchext.core.crx  import CrxDecoder

LICENSE_PATTERNS = {
    "MIT": [
        r"Permission is hereby granted, free of charge, to any person obtaining a copy",
        r"The above copyright notice and this permission notice shall be included in all copies",
    ],
    "Apache-2.0": [
        r"Licensed under the Apache License, Version 2.0",
        r"http://www.apache.org/licenses/LICENSE-2.0",
    ],
    "GPL-3.0": [
        r"GNU General Public License as published by the Free Software Foundation",
        r"either version 3 of the License, or \(at your option\) any later version",
    ],
    "GPL-2.0": [
        r"GNU General Public License as published by the Free Software Foundation",
        r"either version 2 of the License, or \(at your option\) any later version",
    ],
    "BSD-3-Clause": [
        r"Redistribution and use in source and binary forms, with or without modification",
        r"Neither the name of the .* nor the names of its contributors may be used",
    ],
    "BSD-2-Clause": [
        r"Redistribution and use in source and binary forms, with or without modification",
        r"Redistributions in binary form must reproduce the above copyright notice",
    ],
    "ISC": [
        r"Permission to use, copy, modify, and/or distribute this software for any purpose",
    ],
    "MPL-2.0": [
        r"Mozilla Public License Version 2.0",
    ],
}


def scan_licenses(file_path: Path) -> Dict[str, List[str]]:
    """
    Scans an extension archive for license information.
    Returns a dict mapping license names to lists of files where they were found.
    """
    results = {}

    offset = 0
    if file_path.suffix.lower() == ".crx":
        offset = CrxDecoder.get_zip_offset(file_path)

    f = open(file_path, "rb")
    if offset > 0:
        f.seek(offset)

    try:
        with ZipFile(f) as zf:
            # 1. Check package.json
            if "package.json" in zf.namelist():
                try:
                    content = zf.read("package.json").decode("utf-8", errors="ignore")
                    pkg = json.loads(content)
                    if "license" in pkg:
                        lic = pkg["license"]
                        if isinstance(lic, dict):
                            lic = lic.get("type", str(lic))
                        _add_result(results, lic, "package.json")
                except Exception:
                    pass

            # 2. Check LICENSE files
            for filename in zf.namelist():
                if filename.upper().split("/")[-1] in [
                    "LICENSE",
                    "LICENSE.TXT",
                    "COPYING",
                    "NOTICE",
                ]:
                    # Read content to guess license
                    try:
                        content = zf.read(filename).decode("utf-8", errors="ignore")
                        detected = _detect_license_from_text(content)
                        if detected:
                            _add_result(results, detected, filename)
                        else:
                            _add_result(results, "Unknown", filename)
                    except Exception:
                        pass

                # 3. Check headers of source files (limit to top 20 lines)
                elif filename.endswith((".js", ".css", ".html", ".py")):
                    try:
                        with zf.open(filename) as zf_file:
                            # Read first 2KB
                            head = zf_file.read(2048).decode("utf-8", errors="ignore")
                            detected = _detect_license_from_text(head)
                            if detected:
                                _add_result(results, detected, filename)
                    except Exception:
                        pass

    finally:
        f.close()

    return results


def _detect_license_from_text(text: str) -> str:
    for license_name, patterns in LICENSE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return license_name
    return None


def _add_result(results: Dict, license_name: str, filename: str):
    if license_name not in results:
        results[license_name] = []
    if filename not in results[license_name]:
        results[license_name].append(filename)
