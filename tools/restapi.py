from typing import Annotated, Any, Dict
from semantic_kernel.functions import kernel_function
from .base_plugin import BasePlugin

class RestApiPlugin(BasePlugin):
    
    def __init__(self, settings : Dict= {}):

        super().__init__(settings)

        