import logging
import aiohttp

from typing import Annotated, Dict
from semantic_kernel.functions import kernel_function
from configuration import Configuration
from .base_plugin import BasePlugin

class AzureAISearchPlugin(BasePlugin):
    
    def __init__(self, settings : Dict= {}):
        
        config = settings.get("config")
        
        if (config is None):
            self.config = Configuration()
        else:
            self.config = config

        #pull from config first
        self.search_service = self.config.get_value("AZURE_SEARCH_SERVICE")
        self.search_index = self.config.get_value("AZURE_SEARCH_INDEX_NAME")
        self.search_api_version = self.config.get_value("AZURE_SEARCH_API_VERSION", "2024-07-01")
        self.search_api_key = self.config.get_value("AZURE_SEARCH_API_KEY", "")
        
        #check if overriden in settings
        if "search_service" in settings:
            self.search_service = settings["search_service"]

        if "search_index" in settings:
            self.search_index = settings["search_index"]

        if "search_api_version" in settings:
            self.search_api_version = settings["search_api_version"]

        if "search_api_key" in settings:
            self.search_api_key = settings["search_api_key"]
        
        # Build the search endpoint URL.
        self.search_endpoint = (
            f"https://{self.search_service}.search.windows.net/indexes/{self.search_index}/docs/search?api-version={self.search_api_version}"
        )

    async def run(
        self,
        body: Annotated[str, "The request body for the Azure Search API."],
        index_override: Annotated[str, "The index name to override the default index."] = None,
    ) -> str:
        
        if not self.search_service:
            raise Exception("AZURE_SEARCH_SERVICE environment variable is not set.")
        
        search_endpoint = self.search_endpoint
        
        if index_override:
            search_endpoint = (
                f"https://{self.search_service}.search.windows.net/indexes/{index_override}/docs/search?api-version={self.search_api_version}"
            )
        
        # Obtain an access token for the search service.
        if self.search_api_key:
            headers = {
                "Content-Type": "application/json",
                "api-key": self.search_api_key
            }
        else:
            try:
                azure_search_scope = "https://search.azure.com/.default"
                token = self.config.credential.get_token(azure_search_scope).token
            except Exception as e:
                logging.error("Error obtaining Azure Search token.", exc_info=True)
                raise Exception("Failed to obtain Azure Search token.") from e

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(search_endpoint, headers=headers, json=body) as response:
                    if response.status >= 400:
                        text = await response.text()
                        error_message = f"Status code: {response.status}. Error: {text}"
                        logging.error(f"[measures] {error_message}")
                        raise Exception(error_message)
                    result = await response.json()
                    return result
            except Exception as e:
                logging.error("Error during the search HTTP request.", exc_info=True)
                return ''