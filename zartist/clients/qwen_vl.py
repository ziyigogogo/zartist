import os

from zartist import logger
from zartist.abc.clients import OpenAILLMClient
from zartist.utils.image_utils import process_image_reprs


class QwenVLClient(OpenAILLMClient):
    """Client for making requests to Qwen VL Max model"""

    model = "qwen-vl-max-2025-01-25"
    api_key = os.getenv("ALIYUN_API_KEY")
    base_url = os.getenv("ALIYUN_BASE_URL")

    # request parameters
    min_pixels: int = 256 * 256
    max_pixels: int = 1024 * 1024

    # ¥ per 1000 tokens
    prompt_price: float = 0.003
    completion_price: float = 0.009

    def build_messages(self, prompt, image_reprs, history=None, system_prompt=None):
        messages = super().build_messages(prompt, history, system_prompt)
        # load image
        for image in process_image_reprs(image_reprs):
            messages[-1]["content"].append({
                "type": "image_url",
                "min_pixels": self.min_pixels,
                "max_pixels": self.max_pixels,
                "image_url": {
                    "url": image
                }
            })
        # logger.debug(f"messages: {messages}")
        return messages


if __name__ == "__main__":
    client = QwenVLClient()
    # Test with a single image
    llm_resp = client(system_prompt="你是一个嘴巴很贱但是心底善良的贴吧老哥，你会对用户的问题百般抨击，但是最后会得出回答",
                      prompt="图中画了什么？最有可能的地点在世界上的哪个国家的哪个景区？",
                      image_reprs="https://dashscope.oss-cn-beijing.aliyuncs.com/images/dog_and_girl.jpeg")
    logger.debug(llm_resp)
