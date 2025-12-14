from typing import Dict, Any


def get_schema(schema_type: str) -> Dict[str, Any]:
    if schema_type == "config":
        return CONFIG_SCHEMA
    elif schema_type == "audit":
        return AUDIT_SCHEMA
    elif schema_type == "risk":
        return RISK_SCHEMA
    elif schema_type == "history":
        return HISTORY_SCHEMA
    elif schema_type == "scan":
        return SCAN_SCHEMA
    else:
        raise ValueError(f"Unknown schema type: {schema_type}")


# JSON Schema Draft 7 definitions

HISTORY_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "History Entry",
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "timestamp": {"type": "string", "format": "date-time"},
            "action": {"type": "string", "enum": ["download", "extract"]},
            "id": {"type": "string"},
            "browser": {"type": "string"},
            "version": {"type": ["string", "null"]},
            "status": {"type": "string"},
            "path": {"type": ["string", "null"]},
        },
        "required": ["timestamp", "action", "id", "browser", "status"],
    },
}

AUDIT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Audit Report",
    "type": "object",
    "properties": {
        "manifest_version": {"type": "integer"},
        "issues": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "severity": {
                        "type": "string",
                        "enum": ["error", "warning", "info"],
                    },
                    "message": {"type": "string"},
                    "file": {"type": "string"},
                    "line": {"type": ["integer", "null"]},
                },
                "required": ["severity", "message", "file"],
            },
        },
    },
    "required": ["manifest_version", "issues"],
}

RISK_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Risk Report",
    "type": "object",
    "properties": {
        "total_score": {"type": "integer"},
        "max_level": {
            "type": "string",
            "enum": ["Critical", "High", "Medium", "Low", "Safe"],
        },
        "risky_permissions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "permission": {"type": "string"},
                    "score": {"type": "integer"},
                    "level": {"type": "string"},
                    "description": {"type": "string"},
                },
                "required": ["permission", "score", "level", "description"],
            },
        },
        "safe_permissions": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["total_score", "max_level", "risky_permissions", "safe_permissions"],
}

SCAN_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Dependency Scan Report",
    "type": "object",
    "properties": {
        "file": {"type": "string"},
        "libraries": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "version": {"type": "string"},
                    "path": {"type": "string"},
                    "vulnerable": {"type": "boolean"},
                    "advisory": {"type": ["string", "null"]},
                },
                "required": ["name", "version", "path", "vulnerable"],
            },
        },
    },
    "required": ["file", "libraries"],
}

CONFIG_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Configuration",
    "type": "object",
    "properties": {
        "general": {
            "type": "object",
            "properties": {
                "download_dir": {"type": "string"},
                "save_metadata": {"type": "boolean"},
                "extract": {"type": "boolean"},
                "rate_limit_delay": {"type": "number"},
            },
        },
        "batch": {
            "type": "object",
            "properties": {"workers": {"type": "integer", "minimum": 1}},
        },
        "cache": {
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean"},
                "ttl": {"type": "integer", "minimum": 0},
            },
        },
        "rules": {
            "type": "object",
            "properties": {
                "repo_url": {"type": "string"},
                "repo_dir": {"type": "string"},
            },
        },
    },
}
