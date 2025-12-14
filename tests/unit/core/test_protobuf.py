from fetchext.core.protobuf import SimpleProtobuf


def test_read_varint():
    # 150 = 10010110 00000001 (little endian)
    # 150 = 0x96 0x01
    data = b"\x96\x01"
    val, offset = SimpleProtobuf._read_varint(data, 0)
    assert val == 150
    assert offset == 2


def test_parse_simple():
    # Field 1 (00001 010 -> 0x0A), Length 3, "abc"
    data = b"\x0a\x03abc"
    fields = SimpleProtobuf.parse(data)
    assert 1 in fields
    assert fields[1][0] == b"abc"


def test_parse_multiple_fields():
    # Field 1: "a", Field 2: "b"
    # 1 -> 0x0A, len 1, 'a'
    # 2 -> 0x12, len 1, 'b'
    data = b"\x0a\x01a\x12\x01b"
    fields = SimpleProtobuf.parse(data)
    assert fields[1][0] == b"a"
    assert fields[2][0] == b"b"
