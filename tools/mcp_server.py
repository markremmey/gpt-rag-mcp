import os
from semantic_kernel import Kernel
from semantic_kernel.connectors.mcp import MCPSsePlugin

from typing import Annotated, Dict
from semantic_kernel.functions import kernel_function

from .base_plugin import BasePlugin

class McpServerPlugin(BasePlugin):

    plug_in : MCPSsePlugin
    
    def __init__(self, settings : Dict= {}):
        """
        Initialize MCP Server Plugin with the provided settings.
        """
        super().__init__(settings)

        self.name = settings.get("name", "")
        self.description = settings.get("description", "")
        self.url = settings.get("url", "")

        self.plug_in = MCPSsePlugin(
            name=self.name,
            description=self.description,
            url=self.url,
        )