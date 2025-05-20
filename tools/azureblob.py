import inspect
import copy
import datetime

from typing import Annotated, Any, Dict
from semantic_kernel.functions import kernel_function
from connectors import BlobContainerClient, BlobClient

from .base_plugin import BasePlugin
from configuration import Configuration

class AzureBlobPlugin(BasePlugin):
    """
    Azure Blob Storage Plugin
    """

    def __init__(self, settings : Dict= {}):
        from semantic_kernel.functions import kernel_function

        super().__init__(settings)

        self.storage_account = settings["storage_account"]
        self.container_name = settings["container_name"]
        self.blob_container_client = BlobContainerClient(storage_account_base_url=f"https://{self.storage_account}.blob.core.windows.net", 
                                                         container_name=self.container_name,
                                                         credential=self.config.credential)
        
        self.prefix = settings.get("prefix","")
        self.suffix = settings.get("suffix","")
        self.description = settings.get("description","")
        self.description_process_document = settings.get(f"description_process_document",f"Will retrieve documents from the {self.container_name} blob storage container.")
        
        super().reset_kernel_functions(settings)

    async def run(
        self,
        body: Annotated[str, "The request body for Azure Storage API."],
    ) -> str:
        """
        Executes an Azure Storage API request.
        """
        # Call the parent class's run method to perform the search
        return await super().run(body)
        
    @kernel_function(
        name=f"get_blob_documents",
        description="Will retrieve documents from the blob storage container."
    )
    async def process_document(
            self,
            container_name: str,
            path: str = '',
            generate_sas_token: bool = False,
            return_full_path: bool = False
            ) -> Any:
            """
            Get a list of documents from blob storage.
            """
            try:
                self.blob_container_client = BlobContainerClient(storage_account_base_url=f"https://{self.storage_account}.blob.core.windows.net", container_name=container_name, credential=self.config.credential)
                blobs = self.blob_container_client.list_blobs(generate_sas_token=generate_sas_token, path=path)

                response = ''
                for blob in blobs:
                    response += f"Blob name: {blob}\n"
            
                return response
            except Exception as e:
                return f"Error: {str(e)}"
                