from typing import Dict, List, Union
import os
from dotenv import load_dotenv

from openai import OpenAI

from zartist.base.client import BaseLLMClient
from zartist.utils.builtin_utils import fn_timer, normalize_text
from zartist.utils.image_utils import process_image_reprs

# Load environment variables
load_dotenv()

class OpenAIQwenVLClient(BaseLLMClient):
    """Client for making requests to Qwen VL model"""
    # api parameters
    model: str = "qwen-vl-max-2025-01-25"
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
    )

    # ¥ per 1000 tokens
    prompt_price: float = 0.003
    completion_price: float = 0.009

    # request parameters
    min_pixels: int = 128 * 28 * 28
    max_pixels: int = 512 * 28 * 28

    def build_messages(
            self,
            prompt: str,
            valid_images: list[str],
            history: [dict] = None,
            system_prompt: str = "You are a helpful assistant.",
    ) -> [dict]:
        """
        Build messages from prompt and history.

        Args:
            prompt: Text prompt for the model
            valid_images: List of valid image URLs or base64 strings
            history: Previous messages
            system_prompt: System prompt to set model behavior
        Returns:
            List of messages
        """
        # Prepare messages
        messages = [{"role": "system", "content": system_prompt}]
        if history and isinstance(history, list) and all(isinstance(msg, dict) for msg in history):
            # Check if there's a system message at the beginning
            if history[0].get("role", "") == "system":
                messages = history
            else:
                messages += history

        # Add images and prompt in a single user message
        content = []
        for image in valid_images:
            content.append({
                "type": "image_url",
                "min_pixels": self.min_pixels,
                "max_pixels": self.max_pixels,
                "image_url": {"url": image},
            })
        content.append({"type": "text", "text": prompt})
        messages.append({"role": "user", "content": content})

        return messages

    def build_request(self, messages: [dict]) -> dict:
        """
        Build request payload for Qwen VL model.

        Args:
            messages: List of messages

        Returns:
            Request payload
        """
        return {
            "model": self.model,
            "messages": messages,
        }

    def send_request(self, request: Dict) -> Dict:
        """
        Send request to Qwen VL model and get response.

        Args:
            request: Request payload

        Returns:
            Response from Qwen VL model
        """
        if self.client is None:
            self.client = self.build_client()
        return self.client.chat.completions.create(**request).to_dict()

    def parse_answer(self, response: Dict) -> str:
        """
        Parse Qwen VL model response to get answer text.

        Args:
            response: Response from Qwen VL model

        Returns:
            Answer text
        """
        usage = response["usage"]
        content = response["choices"][0]["message"]["content"]

        self.print_usage(usage)
        return normalize_text(content)

    def print_usage(self, usage: Dict) -> str:
        """
        Calculate and format the cost breakdown for a model response.

        Args:
            usage: The usage dictionary from the model response

        Returns:
            A formatted string with the cost breakdown
        """
        prompt_tokens = usage['prompt_tokens']
        completion_tokens = usage['completion_tokens']
        prompt_cost = prompt_tokens * self.prompt_price / 1000
        completion_cost = completion_tokens * self.completion_price / 1000
        total_cost = prompt_cost + completion_cost
        print(
            f"Prompt cost: ¥{prompt_cost:.4f}, Completion cost: ¥{completion_cost:.4f}, Total cost: ¥{total_cost:.4f}"
        )

    @fn_timer
    def query(
            self,
            prompt: str,
            image_reprs: Union[str, List[str]],
            history: [dict] = None,
            **kwargs
    ) -> str:
        """
        Analyze images using Qwen VL model.

        Args:
            prompt: Text prompt for the model
            image_reprs: Single image string or list of image strings. Each can be:
                      1. base64 encoded image string
                      2. URL to image
                      3. Local image file path
            history: Previous messages

        Returns:
            Model response as string
        """
        return super().query(prompt=prompt, valid_images=process_image_reprs(image_reprs), history=history, **kwargs)


if __name__ == "__main__":
    client = OpenAIQwenVLClient()

    llm_resp = client.query(
        prompt="图中画了什么？最有可能的地点在世界上的哪个国家的哪个景区？",
        image_reprs="https://dashscope.oss-cn-beijing.aliyuncs.com/images/dog_and_girl.jpeg",
        system_prompt="你是一个嘴巴很贱但是心底善良的贴吧老哥，你会对用户的问题百般抨击，但是最后会得出回答",
    )
    print(llm_resp)
