from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients"""

    @abstractmethod
    def build_messages(self, prompt: str, history: Optional[List[Dict]] = None) -> List[Dict]:
        """Build messages from prompt and history"""
        pass

    @abstractmethod
    def build_request(self, messages: List[Dict]) -> Dict:
        """Build request payload for specific backend"""
        pass

    @abstractmethod
    def send_request(self, request: Dict) -> Dict:
        """Send request to LLM backend and get response"""
        pass

    @abstractmethod
    def parse_answer(self, response: Dict) -> str:
        """Parse LLM response to get answer text"""
        pass

    def query(self, *args, **kwargs):
        messages = self.build_messages(*args, **kwargs)
        request = self.build_request(messages)
        response = self.send_request(request)
        answer = self.parse_answer(response)
        return answer

    def __call__(self, *args, **kwargs):
        return self.query(*args, **kwargs)
