import logging

from typing import Dict
from semantic_kernel.functions import kernel_function
from configuration import Configuration
from connectors import CosmosDBClient
from tools.base_plugin import BasePlugin
from tools import DocIntelligencePlugin, OpenAIPlugin, AzureBlobPlugin, AzureAISearchPlugin

class CompositePlugin(BasePlugin):
    def __init__(self, settings : Dict= {}):

        super().__init__(settings)

        self.cosmosClient = CosmosDBClient(self.config)

        self.docPlugin : DocIntelligencePlugin = DocIntelligencePlugin(settings)
        self.openAIPlugin : OpenAIPlugin = OpenAIPlugin(settings)
        self.azureBlobPlugin : AzureBlobPlugin = AzureBlobPlugin(settings)
        self.azureAiSearchPlugin : AzureAISearchPlugin = AzureAISearchPlugin(settings)
        
    @kernel_function(
        name="process_blob",
        description="Executes operations against a blob.",
    )
    async def process_blob(self, 
            documentUrl: str):
        """
        Processes a blob URL and returns a summary of the content.
        """

        #get the container name and blob name from the URL
        container_name = documentUrl.split("/")[3]

        logging.info(f"Processing blob in container: {container_name}")

        #get the blob name after the container name
        blob_path = "/".join(documentUrl.split("/")[4:])

        logging.info(f"Blob path: {blob_path}")

        _get_user_context = self._get_user_context()

        #document intelligence can't process url without a SAS token
        sas_token = self.azureBlobPlugin.create_sas_token(container_name, blob_path)

        logging.info(f"SAS Token created for blob: {sas_token}")

        try:
            #get the blob name from the URL
            blob = documentUrl.split("/")[-1]
            if not blob:
                raise ValueError("Invalid document URL provided.")
            
            #remove the query parameters if any
            blob = blob.split("?")[0]
            if not blob:
                raise ValueError("Invalid document URL provided.")
            
            content = await self.docPlugin.process_document(documentUrl + f"?{sas_token}",)

            #determine the type of document
            doc_type_prompt = self.cosmosClient.get_document("prompts", "document_type_prompt")
            doc_type_prompt = doc_type_prompt.get("system_prompt", "")
            doc_type_prompt = doc_type_prompt.replace("{content}", content)
            documentType = self.openAIPlugin.run_llm_model(doc_type_prompt)

            #get the target schema prompt for document type
            schema_prompt = self.cosmosClient.get_document("prompts", f"schema_prompt_{documentType}")
            schema_prompt = doc_type_prompt.get("system_prompt", "")
            schema_prompt = schema_prompt.replace("{content}", content)
            schema = self.openAIPlugin.run_llm_model(schema_prompt)

            #save the result to blob storage
            self.azureBlobPlugin.upload_blob(
                container_name="silver",
                blob_name=f"{documentType}_{blob}.json",
                data=schema
            )

            #add the document to azure ai search
            #self.azureAiSearchPlugin.

            
        except Exception as e:
            logging.error(f"Error processing blob {documentUrl}: {str(e)}")
            return f"Error: {str(e)}"
