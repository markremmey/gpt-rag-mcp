import wikipedia

from typing import Dict
from semantic_kernel.functions import kernel_function
from configuration import Configuration
from .base_plugin import BasePlugin

#https://wikipedia.readthedocs.io/en/latest/quickstart.html

class WikipediaPlugin(BasePlugin):
    def __init__(self, settings : Dict= {}):

        super().__init__(settings)

        self.name = "Wikipedia"
        self.description = "A plugin to search Wikipedia articles."
        self.api_url = "https://en.wikipedia.org/w/api.php"
        self.results = 5

    @kernel_function(
        name="wikipedia_search",
        description="Performs a search on Wikipedia.",
    )
    def search(self, query: str):
        """
        Search Wikipedia for a given query.
        """

        items = wikipedia.search(query, results=self.results)
        return wikipedia.summary(query)