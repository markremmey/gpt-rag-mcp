from typing import Annotated, Any, Dict
from semantic_kernel.functions import kernel_function
from .base_plugin import BasePlugin
from connectors import CosmosDBClient

class CosmosPlugin(BasePlugin):
    
    def __init__(self, settings : Dict= {}):

        super().__init__(settings)

        self.client = CosmosDBClient(settings["config"])

    def connect(self):
        """
        Connect to the Cosmos DB database.
        """
        # Implement the logic to connect to the Cosmos DB database
        pass
    
    def execute_query(self, query: str) -> str:
        """
        Execute a SQL query against the Cosmos DB database.
        """
        # Implement the logic to execute the SQL query
        
        self.client.list_documents()

    @kernel_function(
        name="cosmos_get_document",
        description="Update a document in a cosmos container.",
    )
    async def get_document(self, container, key):
        return await self.client.get_document(container, key)

    @kernel_function(
        name="cosmos_update_document",
        description="Update a document in a cosmos container.",
    )
    async def update_document(self, container, document):
        return await self.client.update_document(container, document)
    
    @kernel_function(
        name="cosmos_create_document",
        description="Create a document from a cosmos container.",
    )
    async def create_document(self, container, key, body=None):
        """
        Create a document in a Cosmos DB container.
        """
        # Implement the logic to create a document
        return await self.client.create_document(container, key, body)

    @kernel_function(
        name="cosmos_list_documents",
        description="Gets documents from a cosmos container.",
    )
    async def list_documents(
        self, 
        container_name: Annotated[str, "The name of the Cosmos DB container."]) -> Any:
        """
        Execute a SQL query against the Cosmos DB database.
        """
        # Implement the logic to execute the SQL query
        
        return await self.client.list_documents(container_name)