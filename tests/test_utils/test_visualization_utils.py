import pytest
from PIL import Image
import json

from zartist.utils.visualization_utils import parse_json_output, draw_bounding_boxes, COLORS


@pytest.fixture
def sample_image():
    """Create a sample test image"""
    return Image.new('RGB', (200, 200), color='white')


@pytest.fixture
def sample_boxes():
    """Create sample bounding box data"""
    boxes = [{"label": "dog", "bbox_2d": [50, 50, 150, 150]}, {"label": "cat", "bbox_2d": [20, 20, 80, 80]}]
    return json.dumps(boxes)


def test_parse_json_output():
    """Test parse_json_output function"""
    # Test with markdown fencing
    json_str = '''```json
    {"key": "value"}
```'''
    assert parse_json_output(json_str) == '{"key": "value"}'

    # Test without markdown fencing
    json_str = '{"key": "value"}'
    assert parse_json_output(json_str) == '{"key": "value"}'

    # Test with multiple code blocks
    json_str = '''Some text
```json
{"key": "value"}
```
More text'''
    assert parse_json_output(json_str) == '{"key": "value"}'


@pytest.mark.skip("Font file not available")
def test_draw_bounding_boxes(sample_image, sample_boxes):
    """Test draw_bounding_boxes function"""
    # Create a temporary font file for testing

    # Test basic functionality
    result = draw_bounding_boxes(sample_image,
                                 sample_boxes,
                                 input_width=200,
                                 input_height=200,
                                 font_path="NotoSansCJK-Regular.ttc",
                                 show=False)
    assert isinstance(result, Image.Image)

    # Test with different image sizes
    large_image = Image.new('RGB', (400, 400), color='white')
    result = draw_bounding_boxes(large_image,
                                 sample_boxes,
                                 input_width=200,
                                 input_height=200,
                                 font_path="NotoSansCJK-Regular.ttc",
                                 show=False)
    assert isinstance(result, Image.Image)


@pytest.mark.skip("Font file not available")
def test_draw_bounding_boxes_invalid(sample_image):
    """Test draw_bounding_boxes with invalid inputs"""
    # Test with invalid JSON
    with pytest.raises(Exception):
        draw_bounding_boxes(sample_image,
                            "invalid json",
                            input_width=200,
                            input_height=200,
                            font_path="NotoSansCJK-Regular.ttc",
                            show=False)

    # Test with empty boxes
    result = draw_bounding_boxes(sample_image,
                                 "[]",
                                 input_width=200,
                                 input_height=200,
                                 font_path="NotoSansCJK-Regular.ttc",
                                 show=False)
    assert isinstance(result, Image.Image)


def test_colors():
    """Test color palette"""
    # Verify we have a non-empty color list
    assert len(COLORS) > 0
    # Verify all colors are valid PIL colors
    for color in COLORS:
        try:
            Image.new('RGB', (1, 1), color=color)
        except ValueError:
            pytest.fail(f"Invalid color: {color}")
