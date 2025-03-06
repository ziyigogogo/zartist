import base64
import os
import pytest
from PIL import Image
import io

from zartist.utils.image_utils import str2pil, pil2b64, process_image_reprs
from zartist.errors import StrParseError


@pytest.fixture
def sample_image():
    """Create a simple test image"""
    img = Image.new('RGB', (100, 100), color='red')
    return img


@pytest.fixture
def sample_image_b64(sample_image):
    """Create a base64 string of the test image"""
    buffered = io.BytesIO()
    sample_image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"


def test_str2pil_base64(sample_image_b64):
    """Test str2pil with base64 input"""
    img = str2pil(sample_image_b64)
    assert isinstance(img, Image.Image)
    assert img.size == (100, 100)


def test_str2pil_url():
    """Test str2pil with URL input"""
    # Skip if no internet connection
    pytest.skip("Requires internet connection")
    url = "https://example.com/test.jpg"  # Replace with a real test image URL
    with pytest.raises(StrParseError):
        str2pil(url)


def test_str2pil_invalid():
    """Test str2pil with invalid inputs"""
    # Test with invalid base64
    with pytest.raises(StrParseError):
        str2pil("data:image/png;base64,invalid")
    
    # Test with non-existent file
    with pytest.raises(StrParseError):
        str2pil("nonexistent.jpg")
    
    # Test with invalid string
    with pytest.raises(StrParseError):
        str2pil("invalid string")


def test_pil2b64(sample_image):
    """Test pil2b64 function"""
    # Test PNG format
    b64_str = pil2b64(sample_image, format="PNG")
    assert b64_str.startswith("data:image/png;base64,")
    
    # Test JPEG format
    b64_str = pil2b64(sample_image, format="JPEG")
    assert b64_str.startswith("data:image/jpeg;base64,")
    
    # Test invalid input
    with pytest.raises(TypeError):
        pil2b64("not an image")


def test_process_image_reprs(sample_image_b64):
    """Test process_image_reprs function"""
    # Test single base64 string
    result = process_image_reprs(sample_image_b64)
    assert len(result) == 1
    assert result[0] == sample_image_b64
    
    # Test list of base64 strings
    result = process_image_reprs([sample_image_b64, sample_image_b64])
    assert len(result) == 2
    assert all(img.startswith("data:image/") for img in result)
    
    # Test with invalid images
    result = process_image_reprs(["invalid string", sample_image_b64])
    assert len(result) == 1
    assert result[0] == sample_image_b64
    
    # Test keep_url parameter
    url = "https://example.com/test.jpg"
    result = process_image_reprs(url, keep_url=True)
    assert len(result) == 1
    assert result[0] == url
