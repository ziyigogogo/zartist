import pytest
from PIL import Image
import pandas as pd

from zartist.utils.composite_utils import str2obj
from zartist.errors import StrParseError


def test_str2obj_auto():
    """Test str2obj with auto type detection"""
    # Test dict auto detection
    assert str2obj('{"a": 1}') == {"a": 1}
    assert str2obj("{'a': 1}") == {"a": 1}
    
    # Test basic Python types
    assert str2obj("[1, 2, 3]") == [1, 2, 3]
    assert str2obj("True") is True
    assert str2obj("42") == 42


def test_str2obj_dict():
    """Test str2obj with explicit dict type"""
    # Test valid dict strings
    assert str2obj('{"a": 1}', target_type="dict") == {"a": 1}
    assert str2obj("{'a': {'b': [1,2,3]}}", target_type="dict") == {"a": {"b": [1,2,3]}}
    
    # Test with non-dict input
    with pytest.raises(StrParseError):
        str2obj("not a dict", target_type="dict")


def test_str2obj_invalid():
    """Test str2obj with invalid inputs"""
    # Test with invalid type
    with pytest.raises(StrParseError):
        str2obj('{"a": 1}', target_type="invalid_type")
    
    # Test with invalid syntax
    with pytest.raises(StrParseError):
        str2obj("{invalid syntax}", target_type="dict")


@pytest.mark.skip("Requires actual image data")
def test_str2obj_pil():
    """Test str2obj with PIL image type"""
    # Note: This test requires actual image data or base64 string
    # Implement when image test data is available
    pass


@pytest.mark.skip("Requires actual DataFrame data")
def test_str2obj_df():
    """Test str2obj with DataFrame type"""
    # Note: This test requires actual DataFrame data
    # Implement when DataFrame test data is available
    pass
