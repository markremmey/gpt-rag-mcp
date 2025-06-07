import inspect
import copy
import datetime

from datetime import datetime, timedelta
from io import IOBase as IO

from typing import Annotated, Any, Dict, Union
from semantic_kernel.functions import kernel_function
from connectors import BlobContainerClient, BlobClient

from azure.storage.blob import BlobServiceClient,BlobSasPermissions, generate_blob_sas

from .base_plugin import BasePlugin
from configuration import Configuration

class AzureBlobPlugin(BasePlugin):
    """
    Azure Blob Storage Plugin
    """
    blob_service_client: BlobServiceClient = None

    def __init__(self, settings : Dict= {}):
        from semantic_kernel.functions import kernel_function

        super().__init__(settings)

        self.storage_account = settings["storage_account"]
        self.container_name = settings["container_name"]
        self.blob_container_client = BlobContainerClient(storage_account_base_url=f"https://{self.storage_account}.blob.core.windows.net", 
                                                         container_name=self.container_name,
                                                         credential=self.config.credential)
        
        self.blob_service_client = BlobServiceClient(account_url=f"https://{self.storage_account}.blob.core.windows.net", credential=self.config.credential)

        
        self.prefix = settings.get("prefix","")
        self.suffix = settings.get("suffix","")
        self.description = settings.get("description","")
        self.description_process_document = settings.get(f"description_process_document",f"Will retrieve documents from the {self.container_name} blob storage container.")
        
        super().reset_kernel_functions(settings)


    def _invalidate_container(self, container_name: str):
        container_client = self.blob_service_client.get_container_client(container_name)
        if not container_client.exists():
            container_client.create_container()

    def _get_container_client(self, container_name=None):
        if container_name:
            full_container_name = (
                f"{self.parent_container_name}/{container_name}"
                if self.parent_container_name
                else container_name
            )
        elif self.parent_container_name is not None and container_name is None:
            full_container_name = self.parent_container_name
        else:
            raise ValueError(
                "Container name must be provided either during initialization or as a function argument."
            )

        container_client = self.blob_service_client.get_container_client(
            full_container_name
        )

        return container_client

    def upload_file(self, container_name: str, blob_name: str, file_path: str):
        blob_client = self._get_container_client(container_name).get_blob_client(
            blob_name
        )

        with open(file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)

    def upload_stream(self, container_name: str, blob_name: str, stream: IO):
        blob_client = self._get_container_client(container_name).get_blob_client(
            blob_name
        )

        blob_client.upload_blob(stream, overwrite=True)

    def upload_text(self, container_name: str, blob_name: str, text: str):
        blob_client = self._get_container_client(container_name).get_blob_client(
            blob_name
        )
        blob_client.upload_blob(text, overwrite=True)

    def download_file(self, container_name: str, blob_name: str, download_path: str):
        blob_client = self._get_container_client(container_name).get_blob_client(
            blob_name
        )
        with open(download_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())

    def download_stream(self, container_name: str, blob_name: str) -> bytes:
        blob_client = self._get_container_client(container_name).get_blob_client(
            blob_name
        )
        stream = blob_client.download_blob().readall()
        return stream

    def download_text(self, container_name: str, blob_name: str) -> str:
        blob_client = self._get_container_client(container_name).get_blob_client(
            blob_name
        )
        text = blob_client.download_blob().content_as_text()
        return text

    def delete_blob(self, container_name: str, blob_name: str):
        blob_client = self._get_container_client(container_name).get_blob_client(
            blob_name
        )
        blob_client.delete_blob()

    def update_blob(
        self, container_name: str, blob_name: str, data: Union[str, IO, bytes]
    ):
        self.upload_blob(container_name, blob_name, data)

    def upload_blob(
        self, container_name: str, blob_name: str, data: Union[str, IO, bytes]
    ):
        blob_client = self._get_container_client(container_name).get_blob_client(
            blob_name
        )
        if isinstance(data, str):
            blob_client.upload_blob(data, overwrite=True)
        elif isinstance(data, bytes):
            blob_client.upload_blob(data, overwrite=True)
        elif hasattr(data, "read"):
            blob_client.upload_blob(data, overwrite=True)
        else:
            raise ValueError("Unsupported data type for upload")

    def create_sas_token(
        self, container_name: str, blob_name: str, expiry: datetime = None
    ) -> str:
        
        if expiry is None:
            expiry = datetime.utcnow() + timedelta(hours=1)
        
        user_delegation_key = self.blob_service_client.get_user_delegation_key(
            key_start_time=datetime.utcnow(),
            key_expiry_time=expiry  # Key expiry in 1 hour
        )

        sas_token = generate_blob_sas(
            account_name=self.storage_account,
            container_name=container_name,
            blob_name=blob_name,
            user_delegation_key=user_delegation_key,
            permission=BlobSasPermissions(read=True),  # Example: Read permission
            expiry=datetime.utcnow() + timedelta(hours=1),  # SAS expiry in 1 hour
        )
        
        return sas_token

        
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
                