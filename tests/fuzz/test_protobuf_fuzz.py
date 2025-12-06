from hypothesis import given, strategies as st
import pytest
from fetchext.protobuf import SimpleProtobuf

@given(st.binary())
def test_fuzz_protobuf_parse(data):
    """
    Fuzz test for SimpleProtobuf.parse.
    It should either return a dict or raise ValueError.
    It should NOT raise IndexError, RecursionError, etc.
    """
    try:
        result = SimpleProtobuf.parse(data)
        assert isinstance(result, dict)
    except ValueError:
        # Expected error for malformed data
        pass
    except Exception as e:
        pytest.fail(f"Unexpected exception: {type(e).__name__}: {e}")
