import json
import logging

from typing import Dict, List, Optional, Type, Dict
from datetime import datetime, timezone
from pydantic import BaseModel
from semantic_kernel.functions import kernel_function

from configuration import Configuration
from .base_plugin import BasePlugin
from models import Citation
from inputs import SearchInput

from azure.cognitiveservices.search.websearch import WebSearchClient
from azure.cognitiveservices.search.websearch.models import SafeSearch
from msrest.authentication import CognitiveServicesCredentials

class BingPlugin (BasePlugin):
    args_schema: Type[BaseModel] = SearchInput
    response_format: str = 'content_and_artifact'
 
    def __init__(self, settings : Dict= {}):

        super().__init__(settings)

        """ Initializes the MLSTool class with the tool configuration,
            exploded objects collection, user identity and platform configuration. """
        
        # Get the Bing search URL and key
        self.bing_search_url = self.config.get_value('BING_URL', 'https://api.bing.microsoft.com/v7.0/search')
        self.bing_api_key = self.config.get_value('BING_API_KEY', '')
        
        # Get search configuration properties
        max_results = self.config.get_value('BING_MAX_RESULTS', 10)
        self.query_filters = self.config.get_value('BING_QUERY_FILTERS', {})
        self.query_prefix = self.config.get_value('BING_QUERY_PREFIX', '')
        self.query_suffix = self.config.get_value('BING_QUERY_SUFFIX', '')

    def _run(self,
            query: str
            ) -> str:
        raise Exception(f"{self.name} does not support synchronous execution. Please use the async version of the tool.")

    @kernel_function(
        name="bing_search",
        description="Performs a search on Bing.",
    )
    async def _arun(self,
        query: str = None
        ) -> str:

        try:
            logging.info(f"[{self.name}] Prompt: {query}")

            query_filters = self.build_query_filters(self.query_filters)
            
            bing_query = f"{self.query_prefix} {query} {self.query_suffix}".strip()
            bing_query += f" {query_filters}" if query_filters else ''

            logging.info(f"[{self.name}] Running Bing search for query: '{bing_query}")

            # Instantiate the client and replace with your endpoint.
            client = WebSearchClient(endpoint=self.bing_search_url, credentials=CognitiveServicesCredentials(self.bing_api_key))

            # Make a request. Replace Yosemite if you'd like.
            web_data = client.web.search(query=query)

            return json.dumps(web_data)
            
        except Exception as e:
            logging.error(f"Error occured trying to retrieve the data using the {self.name}. Error : {e}")
            return ''

    def build_query_filters(self, query_filters: dict):
        filters = '('
        for key, value in query_filters.items():
            if key == 'sites_to_search':
                filters += ' OR '.join([f'site:{site}' for site in value])
            else:
                filters += f' {key}:{value} '
        return filters.strip() + ')'
    
    def get_citations(self, results, bing_query, completion_tokens=0, prompt_tokens=0):
        
        citations = []

        for result in results:
            content_artifact = Citation(id=str(0))
            content_artifact.source = 'BingTool'
            content_artifact.type = 'BingSearchResult'

            if 'snippet' in result:
                content_artifact.content = result.get('link', '')
                content_artifact.filepath = result.get('link', '')
                content_artifact.title = result.get('title', '')
            else:
                content_artifact.content = result.get('Result', '')
                content_artifact.title = result.get('Result', '')

            citations.append(content_artifact)
        citations.append(self.add_tool_content_artifact(bing_query, tool_input=None, prompt_tokens=prompt_tokens, completion_tokens=completion_tokens))
    
        return citations