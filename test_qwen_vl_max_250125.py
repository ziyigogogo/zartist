from PIL import Image
from qwen_vl_utils import smart_resize

from zartist.utils.qwen_vl_client import QwenVLClient, QwenVLConfig
from zartist.utils.visualization_utils import draw_bounding_boxes


def main():
    # Initialize Qwen VL client
    config = QwenVLConfig(
        api_key="sk-b83182bab3f548c1a02ba7f014ab9c43",
    )
    client = QwenVLClient(config)

    # Load and prepare image
    image = Image.open(r"C:\Users\admin\Desktop\dog_and_girl.jpeg")
    width, height = image.size

    prompt = "框出图中的小狗，上衣，和沙滩的位置，用JSON格式回复"
    response = client.analyze_image(image, prompt)

    min_pixels = 512 * 28 * 28
    max_pixels = 2048 * 28 * 28
    # image.thumbnail([640,640], Image.Resampling.LANCZOS)

    input_height, input_width = smart_resize(
        height, width, min_pixels=min_pixels, max_pixels=max_pixels)

    # Analyze image

    # Draw bounding boxes
    draw_bounding_boxes(
        image,
        response,
        input_width,
        input_height,
        font_path=r"c:\Users\admin\Desktop\AlibabaPuHuiTi-3\AlibabaPuHuiTi-3-35-Thin\AlibabaPuHuiTi-3-35-Thin.ttf"
    )


if __name__ == "__main__":
    main()
