import base64
import io
import os
from typing import Union, List

import requests
from PIL import Image

from zartist.errors import StrParseError
from zartist import logger


def load_image(data: bytes) -> "PIL.Image.Image":
    buffer = io.BytesIO(data)
    img = Image.open(buffer)
    img.verify()  # Verify it's an image
    return Image.open(buffer)  # Reopen the image


def str2pil(s: str) -> "PIL.Image.Image":
    """从字符串中提取图像对象"""

    try:
        match s:
            case _ if s.startswith('data:image/'):
                return load_image(base64.b64decode(s.split(',')[1]))
            case _ if s.startswith(('http://', 'https://')):
                return load_image(requests.get(s).content)
            case _ if os.path.isfile(s):
                with open(s, 'rb') as f:
                    return load_image(f.read())
            case _:
                raise TypeError(f"Unsupported str type: {s}")
    except Exception as e:
        raise StrParseError(s, f"@str2pil: an error occurred: {e}")


def pil2b64(img: "PIL.Image.Image", format: str = "PNG") -> str:
    """Convert PIL Image to base64 string

    Args:
        img: PIL Image object
        format: Image format (default: PNG)

    Returns:
        Base64 encoded string with data URI scheme prefix
    """
    if not isinstance(img, Image.Image):
        raise TypeError("Input must be a PIL Image object")
    buffered = io.BytesIO()
    img.save(buffered, format=format)
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/{format.lower()};base64,{img_str}"


def process_image_reprs(image_reprs: Union[str, List[str]], keep_url: bool = True) -> List[str]:
    """
    Process image representations and return a list of valid image URLs or base64 strings.

    Args:
        image_reprs: Single image string or list of image strings. Each can be:
                  1. base64 encoded image string
                  2. URL to image
                  3. Local image file path
        keep_url: If True, keep URLs as is. If False, convert URLs to base64 strings.

    Returns:
        List of valid image URLs or base64 strings
    """
    if isinstance(image_reprs, str):
        image_reprs = [image_reprs]

    valid_images = []
    for s in image_reprs:
        try:
            if not (keep_url and s.startswith(('http://', 'https://'))):
                s = pil2b64(str2pil(s))
            valid_images.append(s)
        except Exception as e:
            logger.error(f"Error processing image: {e}, type: {type(e)}")
            continue
    return valid_images
