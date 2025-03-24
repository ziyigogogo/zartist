import os

from zartist import logger
from zartist.abc.client import OpenAILLMClient


class DeepSeekR1Client(OpenAILLMClient):
    """Client for making requests to DeepSeek R1 model"""

    model = "deepseek-r1"
    api_key = os.getenv("ALIYUN_API_KEY")
    base_url = os.getenv("ALIYUN_BASE_URL")

    # ¥ per 1000 tokens
    prompt_price: float = 0.004
    completion_price: float = 0.016

    def get_content(self, response, return_think=False, **kwargs) -> str:
        dict_resp = response.to_dict()
        think = dict_resp["choices"][0]["message"]["reasoning_content"]
        resp = dict_resp["choices"][0]["message"]["content"]
        self.usage_summary(dict_resp["usage"])
        if return_think:
            return think, resp
        else:
            logger.info(f"DeepSeek R1 think: {think}")
            return resp


if __name__ == "__main__":
    client = DeepSeekR1Client()
    # Test with a single image
    llm_think, llm_resp = client(system="你是一个嘴巴很贱但是心底善良的贴吧老哥，你会对用户的问题百般抨击，但是最后会得出回答",
                                 prompt="你是谁，你知道什么叫德州扑克么？",
                                 return_think=True)
    logger.debug(f"llm_think: {llm_think}")
    logger.debug(f"llm_resp: {llm_resp}")
