import pytest
from utils.platform_utils import _decode_output

def test_decode_output_none():
    assert _decode_output(None) == ""

def test_decode_output_empty_bytes():
    assert _decode_output(b"") == ""

def test_decode_output_string():
    assert _decode_output("hello") == "hello"

def test_decode_output_string_with_null_bytes():
    assert _decode_output("hel\x00lo") == "hello"

def test_decode_output_utf8():
    assert _decode_output("merhaba dünya".encode("utf-8")) == "merhaba dünya"

def test_decode_output_utf8_with_null_bytes():
    assert _decode_output(b"merhaba\x00 d\xc3\xbcnya") == "merhaba dünya"

def test_decode_output_utf16():
    assert _decode_output("merhaba dünya".encode("utf-16")) == "merhaba dünya"

def test_decode_output_cp1254():
    assert _decode_output("merhaba dünya".encode("cp1254")) == "merhaba dünya"

def test_decode_output_invalid_bytes():
    # Provide bytes that cannot be decoded by any of the standard encodings cleanly,
    # or ensure that errors="replace" kicks in as a fallback.
    # Actually, latin-1 decodes almost everything. So it might be caught by latin-1.
    # Let's check with some completely invalid sequence if possible.
    # If latin-1 decodes it, it's fine, we just want to ensure no crash.
    invalid_data = b"\xff\xfe\xff\xff\x00test"
    result = _decode_output(invalid_data)
    assert isinstance(result, str)
    assert "\x00" not in result

def test_decode_output_fallback_replace():
    # To truly hit the fallback, we need something that fails utf-8, utf-16, cp1254, cp1252, latin-1.
    # But latin-1 maps every byte 0-255 to Unicode U+0000 - U+00FF. So latin-1 never raises UnicodeDecodeError.
    # Thus the fallback line `return data.decode("utf-8", errors="replace").replace("\x00", "")` is likely unreachable
    # unless ValueError is raised by decode?
    # Regardless, we should ensure that any random byte sequence is handled without crashing.
    import os
    random_bytes = os.urandom(100)
    result = _decode_output(random_bytes)
    assert isinstance(result, str)
    assert "\x00" not in result
