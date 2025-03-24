from abc import ABC, abstractmethod
import inspect

from zartist.abc.client import BaseLLMClient


class BasePrompter(ABC):
    """
    Base class for prompt tasks
    """
    system = "You are a helpful assistant."

    def render(self, *args, **kwargs):
        prompt_template = inspect.getdoc(self)
        if prompt_template:
            args_and_kwargs = {**{k: v for k, v in zip(inspect.getfullargspec(self.render).args[1:], args)}, **kwargs}
            prompt = prompt_template.format(**args_and_kwargs)
            return prompt
        raise ValueError("Prompt template not found")

    def parse(self, llm_resp):
        return llm_resp


class BaseTask(ABC):
    prompter: BasePrompter = None
    llm_client: BaseLLMClient = None

    def __init__(self, *args, **kwargs) -> None:
        attrs = {**{k: v for k, v in zip(inspect.getfullargspec(self.__init__).args[1:], args)}, **kwargs}
        for k, v in attrs.items():
            setattr(self, k, v)
        if not self.prompter or not isinstance(self.prompter, BasePrompter):
            raise ValueError("Prompter not initialized")
        if not self.llm_client or not isinstance(self.llm_client, BaseLLMClient):
            raise ValueError("Client not initialized")

    def run(self, *args, **kwargs):
        prompt = self.prompter.render(*args, **kwargs)
        llm_resp = self.llm_client.query(system=self.prompter.system,
                                         prompt=prompt,
                                         history=kwargs.get("history", None))
        result = self.prompter.parse(llm_resp)
        return result
