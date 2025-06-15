import base64
import requests

from typing import Dict
from semantic_kernel.functions import kernel_function
from configuration import Configuration

from .model import ModelPlugin
from connectors import AzureOpenAIConnector

class OpenAIPlugin(ModelPlugin):
    def __init__(self, settings : Dict= {}):

        super().__init__(settings)

        self.aoai : AzureOpenAIConnector = AzureOpenAIConnector(self.config, self.settings)

    def run_llm_messages(self,
            messages: dict):
        """
        Runs a LLM model with the given messages.
        """

        _get_user_context = self._get_user_context()

        result = self.aoai.get_completion_messages(
            messages=messages
        )

        return result

    @kernel_function(
        name="run_llm_model",
        description="Runs a LLM model with the given prompt.",
    )
    def run_llm_model(self, 
            user_prompt: str):
        """
        Runs a LLM model with the given prompt.
        """

        _get_user_context = self._get_user_context()

        result = self.aoai.get_completion(
            prompt=user_prompt
        )

        return result
    
    @kernel_function(
        name="run_llm_model_file",
        description="Runs a LLM model with the given prompt.",
    )
    def run_llm_model_file(self, 
            user_prompt: str,
            documentUri: str):
        """
        Runs a LLM model with the given prompt against a file.
        """

        _get_user_context = self._get_user_context()

        #downlaod the file from the URI
        response = requests.get(documentUri)
        if response.status_code != 200:
            raise Exception(f"Failed to download file from {documentUri}. Status code: {response.status_code}")
        
        file_bytes = response.content
        content_type = response.headers.get('Content-Type', 'application/octet-stream')

        return self.run_llm_model_file_bytes(
            user_prompt=user_prompt,
            content_type=content_type,
            file_bytes=file_bytes
        )
    
    def run_llm_model_file_bytes(self, 
            user_prompt: str,
            content_type: str,
            file_bytes: bytes):
        """
        Runs a LLM model with the given prompt against a file bytes.
        """

        b64 = base64.b64encode(file_bytes)

        messages = [
            {
                "role": "developer",
                "content": user_prompt
            },
            {
                "role": "user",
                "content": [
                    {
                        "type" : "text",
                        "text" : user_prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{content_type};base64," + b64.decode('utf-8')
                        }
                    },
                    {
                        "type": "text",
                        "text": "\n"
                    }
                ]
            }
        ]

        result = self.run_llm_messages(messages)

        return result