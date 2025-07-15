import pydantic
import inspect
import copy
import logging

from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    Dict,
    Callable,
    Literal,
    Optional,
    TypeVar,
    Union,
    cast,
    get_args,
    get_origin,
    get_type_hints,    
)
from abc import ABC, abstractmethod
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    PydanticDeprecationWarning,
    SkipValidation,
    ValidationError,
    model_validator,
    validate_arguments,
)
from contextvars import ContextVar
from starlette.requests import Request
from functools import wraps
from semantic_kernel.functions import kernel_function
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

from azure.identity import get_bearer_token_provider
from configuration import Configuration

from middleware.authentication_middleware import get_request

TypeBaseModel = Union[type[BaseModel], type[pydantic.BaseModel]]

ArgsSchema = Union[TypeBaseModel, dict[str, Any]]

class BasePlugin():

    settings : Dict = {}
    config : Configuration = None

    has_oauth_endpoint: bool = False
    oauth_endpoint : str = None

    def handle_oauth_token(scope, send, receive):
        raise NotImplementedError("OAuth handling is not implemented for this plugin.")

    def handle_oauth_authorize(scope, send, receive):
        raise NotImplementedError("OAuth handling is not implemented for this plugin.")

    def __init__(self, settings : Dict= {}):

        logging.info(f"Creating ${__name__}")

        self.settings = settings
        self.config = settings["config"]

        if self.config is None:
            self.config = Configuration()

        self.aoai_resource = self.config.get_value('AZURE_OPENAI_RESOURCE', 'openai')
        self.chat_deployment = self.config.get_value('AZURE_OPENAI_CHATGPT_DEPLOYMENT', 'chat')
        self.model = self.config.get_value('AZURE_OPENAI_CHATGPT_MODEL', 'gpt-4o')
        self.api_version = self.config.get_value('AZURE_OPENAI_API_VERSION', '2024-10-21')
        self.max_tokens = int(self.config.get_value('AZURE_OPENAI_MAX_TOKENS', 10000))
        self.temperature = float(self.config.get_value('AZURE_OPENAI_TEMPERATURE', 0.7))

        # Autogen agent configuration (base to be overridden)
        self.agents = []
        self.terminate_message = "TERMINATE"
        self.max_rounds = int(self.config.get_value('MAX_ROUNDS', 8))
        self.selector_func = None
        self.context_buffer_size = int(self.config.get_value('CONTEXT_BUFFER_SIZE', 30))
        self.text_only=False 
        self.optimize_for_audio=False

    response_format: str = 'content_and_artifact'
    
    name: str
    """The unique name of the tool that clearly communicates its purpose."""
    
    description: str
    """Used to tell the model how/when/why to use the tool.

    You can provide few-shot examples as a part of the description.
    """

    args_schema: Annotated[Optional[ArgsSchema], SkipValidation()] = Field(
        default=None, description="The tool schema."
    )

    def _get_user_context(self) -> str:
        """
        Get the user context for the plugin.

        This method is a placeholder and should be overridden in subclasses
        to provide the actual user context.
        """
        self.request = get_request()

        if self.request is not None:
            user_context = self.request.get("user_context", None)
            if user_context is not None:
                return user_context

    def _get_model_client(self, response_format=None):
        """
        Set up the configuration for the Azure OpenAI language model client.

        Initializes the `AzureOpenAIChatCompletionClient` with the required settings for
        interaction with Azure OpenAI services.
        """
        token_provider = get_bearer_token_provider(
            self.config.credential,
            "https://cognitiveservices.azure.com/.default"
        )
        return AzureChatCompletion(
            deployment_name=self.chat_deployment,
            #model=self.model,
            endpoint=f"https://{self.aoai_resource}.openai.azure.com",
            ad_token_provider=token_provider,
            #api_version=self.api_version,
            #temperature=self.temperature,
            #max_tokens=self.max_tokens,
            #response_format=response_format,
            #parallel_tool_calls=False
        )

    def reset_kernel_functions(self, settings : Dict = {}):
        for name, oldMethod in inspect.getmembers(self, predicate=inspect.ismethod):        
            method = copy.copy(oldMethod)
            
            methodName = method.__name__
            if hasattr(method, '__kernel_function_description__'):
                methodDescription = method.__getattribute__('__kernel_function_description__')
                method.__func__.__setattr__('__kernel_function_description__', settings.get(f"{methodName}_description", methodDescription))

            if hasattr(method, '__kernel_function_name__'):
                methodDescription = method.__getattribute__('__kernel_function_name__')
                method.__func__.__setattr__('__kernel_function_name__', f"{self.prefix}{methodName}{self.suffix}")
                setattr(self, f"{self.prefix}{methodName}{self.suffix}", method)
