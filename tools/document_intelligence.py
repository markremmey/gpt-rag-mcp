import asyncio
import json
import logging

from typing import Annotated, Any, Dict
from semantic_kernel.functions import kernel_function
from configuration import Configuration
from connectors import AzureOpenAIConnector
from .base_plugin import BasePlugin
from connectors import DocumentIntelligenceClient

class DocIntelligencePlugin(BasePlugin):
    """
    Document Intelligence Plugin
    """

    def __init__(self, settings : Dict= {}):
        super().__init__(settings)
        self.prompt = settings.get("prompt","")
        self.targetSchema = settings.get("targetSchema","")

        self.client = DocumentIntelligenceClient(settings["config"])
        self.openai = AzureOpenAIConnector(settings["config"])

    async def run(
        self,
        body: Annotated[str, "The request body Document Intelligence API."],
    ) -> str:
        """
        Executes a document intelligence request.
        """
        # Call the parent class's run method to perform the search
        return await super().run(body)
    
    @kernel_function(
        name="docInt_process_document_url",
        description="Will process a document using Document Intelligence and return a json version of the document.",
    )
    async def process_document(self,
        documentUrl: Annotated[str, "The URL of the document."]
        ) -> Any:
        """
        Process a document using the Document Intelligence API.
        """

        logging.info(f"[docInt_process_document_url] Processing document: {documentUrl}")

        try:
            data, error = self.client.analyze_document_from_blob_url(documentUrl)

            if len(error) > 0:
                return f"Error: {error}"
            
            if 'paragraphs' in data:
                paragraphs = data["paragraphs"]

                content = ''

                for paragraph in paragraphs:
                    content += paragraph["content"] + "\n"

                return content
            
        except Exception as e:
            return f"Error: {str(e)}"
        
    @kernel_function(
        name="docInt_process_document_text",
        description="Will process text and return a matching schema of the document.",
    )
    async def process_document_text_with_schema(self,
        documentText: Annotated[str, "The text of the document."]
        ) -> Any:
        """
        Process a document using the Document Intelligence API.
        """

        logging.info(f"[docInt_process_document_text] Processing document: {documentText}")

        try:
            if self.prompt:
                self.prompt = self.prompt.replace("{targetSchema}", self.targetSchema)
                # Use the prompt to get the result
                result = self.openai.get_completion(
                    f"{self.prompt}\n\nDOCUMENT TEXT:\n\n{documentText}",
                    max_tokens=800,
                    retry_after=True
                )
                return result
            
        except Exception as e:
            return f"Error: {str(e)}"
        
    @kernel_function(
        name="docInt_process_document_json",
        description="Will process json and return a matching schema of the document.",
    )
    async def process_document_json_with_schema(self,
        documentJson: Annotated[str, "The JSON of the document."]
        ) -> Any:
        """
        Process a document using the Document Intelligence API.
        """

        logging.info(f"[process_document_json_with_schema] Processing document: {documentJson}")

        try:
            if self.prompt:
                self.prompt = self.prompt.replace("{targetSchema}", self.targetSchema)
                # Use the prompt to get the result
                result = self.openai.get_completion(
                    f"{self.prompt}\n\nDOCUMENT JSON:\n\n{documentJson}",
                    max_tokens=800,
                    retry_after=True
                )
                return result
                        
        except Exception as e:
            return f"Error: {str(e)}"