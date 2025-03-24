from abc import ABC, abstractmethod
from zartist.utils import fn_timer
from zartist import logger
import inspect


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients"""

    def __init__(self, *args, **kwargs):
        attrs = {**{k: v for k, v in zip(inspect.getfullargspec(self.__init__).args[1:], args)}, **kwargs}
        for k, v in attrs.items():
            setattr(self, k, v)
        self.client = self.build_client()

    @abstractmethod
    def build_client(self) -> object:
        """Build client for specific backend"""
        raise NotImplementedError

    @abstractmethod
    def build_messages(self, prompt: str, history: list[dict] | None = None) -> list[dict]:
        """Build messages from prompt and history"""
        raise NotImplementedError

    @abstractmethod
    def build_request(self, messages: list[dict]) -> dict:
        """Build request payload for specific backend"""
        raise NotImplementedError

    @abstractmethod
    def send_request(self, request: dict) -> dict:
        """Send request to LLM backend and get response"""
        raise NotImplementedError

    @abstractmethod
    def get_content(self, response: dict) -> str:
        """Get answer text from LLM response"""
        raise NotImplementedError

    def query(self, *args, **kwargs):
        messages = self.build_messages(*args, **kwargs)
        request = self.build_request(messages)
        response = self.send_request(request)
        content = self.get_content(response, **kwargs)
        return content

    @fn_timer()
    def debug_query(self, *args, **kwargs):
        return self.query(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        return self.query(*args, **kwargs)


class OpenAILLMClient(BaseLLMClient):
    """Client for making requests to OpenAI format API"""

    def build_client(self) -> object:
        if hasattr(self, "client") and self.client:
            return self.client
        from openai import OpenAI
        return OpenAI(api_key=self.api_key, base_url=self.base_url)

    def build_messages(self, prompt, system=None, history=None, **kwargs):
        system = system or "You are a helpful assistant."
        messages = [{"role": "system", "content": system}]
        if history:
            messages = history if history[0].get("role", "") == "system" else messages + history
        messages.append({"role": "user", "content": [{"type": "text", "text": prompt}]})
        print("messages", messages)
        return messages

    def build_request(self, messages: list[dict]) -> dict:
        return {"model": self.model, "messages": messages}

    def send_request(self, request: dict) -> dict:
        return self.client.chat.completions.create(**request)

    def usage_summary(self, usage: dict) -> str:
        prompt_tokens = usage["prompt_tokens"]
        completion_tokens = usage["completion_tokens"]
        prompt_cost = prompt_tokens * self.prompt_price / 1000
        completion_cost = completion_tokens * self.completion_price / 1000
        total_cost = prompt_cost + completion_cost
        logger.info(
            f"Prompt({prompt_tokens} tokens): ¥{prompt_cost:.4f}, Completion({completion_tokens} tokens): ¥{completion_cost:.4f}, Total: ¥{total_cost:.4f}"
        )

    def get_content(self, response, **kwargs) -> str:
        dict_resp = response.to_dict()
        # logger.debug(f"Response: {dict_resp}")
        self.usage_summary(dict_resp["usage"])
        return dict_resp["choices"][0]["message"]["content"]
