from typing import Dict
from semantic_kernel.functions import kernel_function
from configuration import Configuration

from .base_plugin import BasePlugin
from connectors import AzureOpenAIConnector

class GraphRagPlugin(BasePlugin):
    def __init__(self, settings : Dict= {}):

        super().__init__(settings)

        self.aoai : AzureOpenAIConnector = AzureOpenAIConnector(self.config)

    @kernel_function(
        name="run_graph_query",
        description="Runs a graph query with the given prompt.",
    )
    def search(self, 
        user_prompt: str):
        """
        Runs a graph query with the given prompt.
        """

        _get_user_context = self._get_user_context()

        pass