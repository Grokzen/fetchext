from fetchext.utils import sanitize_filename


def test_sanitize_filename_basic():
    assert sanitize_filename("test.txt") == "test.txt"
    assert sanitize_filename("My File.txt") == "My File.txt"


def test_sanitize_filename_illegal_chars():
    # Windows illegal chars: < > : " / \ | ? *
    assert sanitize_filename("test<file>.txt") == "test_file_.txt"
    assert sanitize_filename("test:file.txt") == "test_file.txt"
    assert sanitize_filename('test"file.txt') == "test_file.txt"
    assert sanitize_filename("test/file.txt") == "test_file.txt"
    assert sanitize_filename("test\\file.txt") == "test_file.txt"
    assert sanitize_filename("test|file.txt") == "test_file.txt"
    assert sanitize_filename("test?file.txt") == "test_file.txt"
    assert sanitize_filename("test*file.txt") == "test_file.txt"


def test_sanitize_filename_control_chars():
    assert sanitize_filename("test\x00file.txt") == "test_file.txt"
    assert sanitize_filename("test\nfile.txt") == "test_file.txt"


def test_sanitize_filename_reserved_names():
    assert sanitize_filename("CON") == "CON_"
    assert sanitize_filename("nul") == "nul_"  # Case insensitive check
    assert sanitize_filename("com1") == "com1_"
    assert sanitize_filename("con.txt") == "con.txt_"  # Should be sanitized now


def test_sanitize_filename_length():
    long_name = "a" * 300 + ".txt"
    sanitized = sanitize_filename(long_name)
    assert len(sanitized) == 255
    assert sanitized.endswith(".txt")

    long_ext = "test." + "a" * 300
    sanitized = sanitize_filename(long_ext)
    assert len(sanitized) == 255
    # Should be truncated
