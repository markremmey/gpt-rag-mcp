from typing import Annotated, Any, Dict
from semantic_kernel.functions import kernel_function
from .base_plugin import BasePlugin

class ExcelPlugin(BasePlugin):
    
    def __init__(self, settings : Dict= {}):

        super().__init__(settings)

        self.location = settings.get("location","")
        self.location_type = settings.get("location_type","blob")

    def download_file(self, file_name: str) -> str:
        """
        Download files from the specified location.
        """
        # Implement the logic to download files from the specified location
        pass

    def set_cell_value(self, file_name: str, sheet_name: str, cell: str, value: Any) -> None:
        """
        Set the value of a specific cell in an Excel file.
        """
        # Implement the logic to set the cell value
        pass