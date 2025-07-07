import os
from semantic_kernel import Kernel
from semantic_kernel.connectors.mcp import MCPSsePlugin

from typing import Annotated, Dict, List
from semantic_kernel.functions import kernel_function

from .base_plugin import BasePlugin
from .openai import OpenAIPlugin

class FollowupPlugin(BasePlugin):
    
    def __init__(self, settings : Dict= {}):
        """
        Initialize MCP Server Plugin with the provided settings.
        """
        super().__init__(settings)

        self.name = settings.get("name", "")
        self.description = settings.get("description", "")
        self.url = settings.get("url", "")

        self.aoai = OpenAIPlugin(settings)

        self.single_prompt = """
        You are a follow-up question generator. Based on the user's input, generate a relevant follow-up question that can help clarify or expand the conversation.

        The question should be concise and directly related to the user's input.
        
        CONTEXT:
        
        {context}
        """

        self.double_prompt = """
        You are a follow-up question generator. Based on the user's input, generate a relevant follow-up question that can help clarify or expand the conversation.

        The question should be concise and directly related to the user's input.
        
        CONTEXT:
        
        {context}
        """

    @kernel_function(
        name="create_followup",
        description="Create a follow-up question based on user input."
    )
    def create_followup(self, user_input: str) -> List[str]:
        """
        Follow up on a user's input by sending it to the MCP server.
        """

        final_prompt = self.single_prompt.replace("{context}", user_input)

        response = self.aoai.run_llm_model(final_prompt)

        return response.split("\n") if response else []
    
    @kernel_function(
        name="create_two_followup",
        description="Create two follow-up questions based on user input."
    )
    def create_two_followup(self, user_input: str) -> List[str]:
        """
        Follow up on a user's input by sending it to the MCP server.
        """

        final_prompt = self.double_prompt.replace("{context}", user_input)

        response = self.aoai.run_llm_model(final_prompt)

        return response.split("\n") if response else []