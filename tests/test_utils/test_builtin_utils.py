import pytest

from zartist.utils.builtin_utils import fn_timer, str2dict, clean_text
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


def test_fn_timer():
    """Test fn_timer decorator"""

    @fn_timer
    def sample_function():
        return "test"

    @fn_timer(n_repeats=2)
    def sample_function_with_repeats():
        return "test"

    # Test basic functionality
    assert sample_function() == "test"
    # Test with repeats
    assert sample_function_with_repeats() == "test"
