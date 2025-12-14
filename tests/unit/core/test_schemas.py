import json
import pytest
from fetchext.data.schemas import get_schema


def test_get_schema_valid():
    for schema_type in ["config", "audit", "risk", "history", "scan"]:
        schema = get_schema(schema_type)
        assert isinstance(schema, dict)
        assert "$schema" in schema
        # Verify it's serializable
        json.dumps(schema)


def test_get_schema_invalid():
    with pytest.raises(ValueError):
        get_schema("invalid_type")


def test_config_schema_structure():
    schema = get_schema("config")
    assert "properties" in schema
    assert "general" in schema["properties"]
    assert "batch" in schema["properties"]


def test_history_schema_structure():
    schema = get_schema("history")
    assert schema["type"] == "array"
    assert "items" in schema
    assert "properties" in schema["items"]
    assert "timestamp" in schema["items"]["properties"]
