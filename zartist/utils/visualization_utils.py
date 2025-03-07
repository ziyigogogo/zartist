"""
Visualization utilities for displaying bounding boxes, points, and other annotations on images.
"""

import ast
import json
from typing import Dict, List, Tuple, Union

from PIL import Image, ImageDraw, ImageFont, ImageColor

from zartist import logger

# Define color palette
COLORS = [
    'red',
    'green',
    'blue',
    'yellow',
    'orange',
    'pink',
    'purple',
    'brown',
    'gray',
    'beige',
    'turquoise',
    'cyan',
    'magenta',
    'lime',
    'navy',
    'maroon',
    'teal',
    'olive',
    'coral',
    'lavender',
    'violet',
    'gold',
    'silver',
] + [colorname for (colorname, _) in ImageColor.colormap.items()]


def parse_json_output(json_output: str) -> str:
    """
    Parse JSON output by removing markdown fencing.
    
    Args:
        json_output: JSON string potentially containing markdown fencing
        
    Returns:
        Clean JSON string
    """
    lines = json_output.splitlines()
    for i, line in enumerate(lines):
        if line == "```json":
            json_output = "\n".join(lines[i + 1:])
            json_output = json_output.split("```")[0]
            break
    return json_output.strip()


def draw_bounding_boxes(image: Image.Image,
                        bounding_boxes: str,
                        input_width: int,
                        input_height: int,
                        font_path: str = "NotoSansCJK-Regular.ttc",
                        font_size: int = 14,
                        line_width: int = 4,
                        show: bool = True) -> Image.Image:
    """
    Draw bounding boxes on an image with labels.
    
    Args:
        image: PIL Image object
        bounding_boxes: JSON string containing bounding box data
        input_width: Original input width for coordinate normalization
        input_height: Original input height for coordinate normalization
        font_path: Path to font file for labels
        font_size: Font size for labels
        line_width: Width of bounding box lines
        show: Whether to display the image
        
    Returns:
        PIL Image with drawn bounding boxes
    """
    width, height = image.size
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_path, size=font_size)

    # Parse bounding boxes
    bounding_boxes = parse_json_output(bounding_boxes)
    try:
        boxes = ast.literal_eval(bounding_boxes)
    except Exception:
        end_idx = bounding_boxes.rfind('"}') + len('"}')
        truncated_text = bounding_boxes[:end_idx] + "]"
        boxes = ast.literal_eval(truncated_text)

    # Draw boxes
    for i, box in enumerate(boxes):
        color = COLORS[i % len(COLORS)]

        # Convert normalized coordinates
        y1 = int(box["bbox_2d"][1] / input_height * height)
        x1 = int(box["bbox_2d"][0] / input_width * width)
        y2 = int(box["bbox_2d"][3] / input_height * height)
        x2 = int(box["bbox_2d"][2] / input_width * width)

        # Ensure correct coordinate order
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)

        # Draw box
        draw.rectangle(((x1, y1), (x2, y2)), outline=color, width=line_width)

        # Draw label if present
        if "label" in box:
            draw.text((x1 + 8, y1 + 6), box["label"], fill=color, font=font)

    if show:
        image.show()
    return image


if __name__ == "__main__":
    json_str = '''```json
    {"key": "value"}
    ```'''
    if json_str:
        logger.info(parse_json_output(json_str))
