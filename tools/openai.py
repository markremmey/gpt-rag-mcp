from typing import Dict
from semantic_kernel.functions import kernel_function
from configuration import Configuration

from .model import ModelPlugin
from connectors import AzureOpenAIConnector

class OpenAIPlugin(ModelPlugin):
    def __init__(self, settings : Dict= {}):

        super().__init__(settings)

        self.aoai : AzureOpenAIConnector = AzureOpenAIConnector(self.config)

    @kernel_function(
        name="run_llm_model",
        description="Runs a LLM model with the given prompt.",
    )
    def run_llm_model(self, 
            user_prompt: str):
        """
        Runs a LLM model with the given prompt.
        """

        _get_user_context = self._get_user_context()

        result = self.aoai.get_completion(
            prompt=user_prompt
        )

        return result