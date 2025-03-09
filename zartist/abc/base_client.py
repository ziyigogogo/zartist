from abc import ABC, abstractmethod

from zartist.utils.builtin_utils import clean_text
from zartist import logger


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients"""

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
    def parse_answer(self, response: dict) -> str:
        """Parse LLM response to get answer text"""
        raise NotImplementedError

    def query(self, *args, **kwargs):
        if not hasattr(self, "client"):
            self.build_client()
        messages = self.build_messages(*args, **kwargs)
        request = self.build_request(messages)
        response = self.send_request(request)
        answer = self.parse_answer(response)
        return answer

    def __call__(self, *args, **kwargs):
        return self.query(*args, **kwargs)


class OpenAIClient(BaseLLMClient):
    """Client for making requests to OpenAI API"""

    @property
    def client(self):
        if not hasattr(self, "_client"):
            from openai import OpenAI
            self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        return self._client

    def build_request(self, messages: list[dict]) -> dict:
        return {"model": self.model, "messages": messages}

    def send_request(self, request: dict) -> dict:
        return self.client.chat.completions.create(**request).to_dict()

    def usage_summary(self, usage: dict) -> str:
        """
        Calculate and format the cost breakdown for a model response.
        Args:
            usage: The usage dictionary from the model response
        Returns:
            A formatted string with the cost breakdown
        """
        prompt_tokens = usage["prompt_tokens"]
        completion_tokens = usage["completion_tokens"]
        prompt_cost = prompt_tokens * self.prompt_price / 1000
        completion_cost = completion_tokens * self.completion_price / 1000
        total_cost = prompt_cost + completion_cost
        logger.info(f"Prompt: ¥{prompt_cost:.4f}, Completion: ¥{completion_cost:.4f}, Total: ¥{total_cost:.4f}")

    def parse_answer(self, response: dict) -> str:
        self.usage_summary(response["usage"])
        return clean_text(response["choices"][0]["message"]["content"])
