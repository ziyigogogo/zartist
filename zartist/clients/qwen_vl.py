import os
import logging

from dotenv import load_dotenv

from zartist import logger
from zartist.abc.base_client import OpenAIClient
from zartist.utils.image_utils import process_image_reprs


class AliQwenVLClient(OpenAIClient):
    """Client for making requests to Qwen VL Max model"""

    model = "qwen-vl-max-2025-01-25"
    api_key = os.getenv("ALIYUN_API_KEY")
    base_url = os.getenv("ALIYUN_BASE_URL")

    # ¥ per 1000 tokens
    prompt_price: float = 0.003
    completion_price: float = 0.009

    # request parameters
    min_pixels: int = 128 * 28 * 28
    max_pixels: int = 512 * 28 * 28

    def build_messages(self, prompt, image_reprs, history=None, system_prompt="You are a helpful assistant."):
        # Prepare messages
        messages = [{"role": "system", "content": system_prompt}]
        if (history and isinstance(history, list) and all(isinstance(msg, dict) for msg in history)):
            # Check if there's a system message at the beginning
            if history[0].get("role", "") == "system":
                messages = history
            else:
                messages += history

        # Add images and prompt in a single user message
        content = []
        for image in process_image_reprs(image_reprs):
            content.append({
                "type": "image_url",
                "min_pixels": self.min_pixels,
                "max_pixels": self.max_pixels,
                "image_url": {
                    "url": image
                }
            })
        content.append({"type": "text", "text": prompt})
        messages.append({"role": "user", "content": content})
        return messages


if __name__ == "__main__":
    client = AliQwenVLClient()

    image_reprs = "https://dashscope.oss-cn-beijing.aliyuncs.com/images/dog_and_girl.jpeg"

    # Test with a single image
    llm_resp = client.query(
        prompt="图中画了什么？最有可能的地点在世界上的哪个国家的哪个景区？",
        image_reprs=image_reprs,
        system_prompt="你是一个嘴巴很贱但是心底善良的贴吧老哥，你会对用户的问题百般抨击，但是最后会得出回答",
    )
    logger.debug(llm_resp)
