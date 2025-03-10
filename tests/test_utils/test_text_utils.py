import pytest

from zartist.utils.text_utils import str2dict, clean_text
from zartist.errors import StrParseError


def test_str2dict_valid_json():
    """Test str2dict with valid JSON input"""
    # Test simple dict
    assert str2dict('{"a": 1}') == {"a": 1}
    # Test nested dict
    assert str2dict('{"a": {"b": [1,2,3]}}') == {"a": {"b": [1, 2, 3]}}
    # Test with whitespace
    assert str2dict('  {"a": 1}  ') == {"a": 1}


def test_str2dict_non_json():
    """Test str2dict with non-JSON but valid Python dict strings"""
    # Test with single quotes
    assert str2dict("{'a': 1}") == {"a": 1}
    # Test with nested structure
    assert str2dict("{'a': {'b':[1,2,3]}}") == {"a": {"b": [1, 2, 3]}}
    # Test with mixed quotes
    assert str2dict("{'a': \"b\"}") == {"a": "b"}


def test_str2dict_invalid():
    """Test str2dict with invalid inputs"""
    # Test with invalid syntax
    with pytest.raises(StrParseError):
        str2dict("{a: 1}")
    # Test with empty string
    with pytest.raises(StrParseError):
        str2dict("")


def test_normalize_text():
    """Test normalize_text function"""
    # Test basic whitespace normalization
    assert clean_text("  hello   world  ") == "hello world"
    # Test newlines and tabs
    assert clean_text("hello\nworld\t!") == "hello world !"
    # Test multiple spaces between words
    assert clean_text("hello     world") == "hello world"
    # Test empty string
    assert clean_text("") == ""
    # Test string with only whitespace
    assert clean_text("   ") == ""
