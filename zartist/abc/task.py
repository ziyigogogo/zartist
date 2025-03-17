from abc import ABC, abstractmethod
import inspect


class BasePromptTask(ABC):
    """
    Base class for prompt tasks
    """

    client = None

    def __init__(self, client=None):
        if client is not None:
            self.client = client

    def render_prompt(self, *args, **kwargs):
        prompt_template = inspect.getdoc(self)
        if prompt_template:
            args_and_kwargs = {
                **{
                    k: v for k, v in zip(inspect.getfullargspec(self.render_prompt).args[1:], args)
                },
                **kwargs
            }
            prompt = prompt_template.format(**args_and_kwargs)
            return prompt
        raise ValueError("Prompt template not found")

    def run(self, *args, **kwargs):
        assert self.client is not None, "Client not initialized"
        prompt = self.render_prompt(*args, **kwargs)
        llm_resp = self.client.query(prompt, **kwargs)
        result = self.formt_resp(llm_resp)
        return result

    @abstractmethod
    def formt_resp(self, llm_resp):
        raise NotImplementedError
