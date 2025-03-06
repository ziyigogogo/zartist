from abc import ABC, abstractmethod


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
        messages = self.build_messages(*args, **kwargs)
        request = self.build_request(messages)
        response = self.send_request(request)
        answer = self.parse_answer(response)
        return answer

    def __call__(self, *args, **kwargs):
        return self.query(*args, **kwargs)
