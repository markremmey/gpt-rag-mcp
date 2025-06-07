from typing import Dict, Any
from .base_plugin import BasePlugin

class ModelPlugin(BasePlugin):

    def __init__(self, settings : Dict= {}):

        super().__init__(settings)

    