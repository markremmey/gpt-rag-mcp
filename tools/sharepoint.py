from typing import Annotated, Dict
from semantic_kernel.functions import kernel_function

from .base_plugin import BasePlugin

class SharePointPlugin(BasePlugin):
    
    def __init__(self, settings : Dict= {}):
        """
        Initialize the SharePoint Plugin with the provided settings.
        """
        super().__init__(settings)