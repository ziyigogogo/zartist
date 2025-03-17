import os

from zartist import logger
from zartist.abc.client import OpenAILLMClient
from zartist.utils.image_utils import process_image_reprs


class QwenMaxClient(OpenAILLMClient):
    """Client for making requests to Qwen Max model"""

    model = "qwen-max-2025-01-25"
    api_key = os.getenv("ALIYUN_API_KEY")
    base_url = os.getenv("ALIYUN_BASE_URL")

    # ¥ per 1000 tokens
    prompt_price: float = 0.0024
    completion_price: float = 0.0096


if __name__ == "__main__":
    client = QwenMaxClient()
    # Test with a single image
    llm_resp = client(system_prompt="你是一个嘴巴很贱但是心底善良的贴吧老哥，你会对用户的问题百般抨击，但是最后会得出回答", prompt="你是谁，你知道什么叫德州扑克么？")
    logger.debug(llm_resp)
