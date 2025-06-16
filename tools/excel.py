from typing import Annotated, Any, Dict
from semantic_kernel.functions import kernel_function
from .base_plugin import BasePlugin

from openpyxl import load_workbook

class ExcelPlugin(BasePlugin):
    
    def __init__(self, settings : Dict= {}):

        super().__init__(settings)

        self.location = settings.get("location","")
        self.location_type = settings.get("location_type","blob")
        self.location_path = settings.get("location_path","/")

    def download_file(self, file_name: str) -> str:
        """
        Download files from the specified location.
        """
        # Implement the logic to download files from the specified location
        
        # For example, if using Azure Blob Storage:
        blob_client = BlobClient.from_blob_url(f"https://{self.location}.blob.core.windows.net/{self.location_path}/{file_name}")
        with open(file_name, "wb") as file:
           blob_data = blob_client.download_blob()
           file.write(blob_data.readall())

    def set_cell_value(self, 
                       file_name: str, 
                       sheet_name: str = None, 
                       cell: str = None, 
                       value: Any = None) -> None:
        """
        Set the value of a specific cell in an Excel file.
        """
        # Implement the logic to set the cell value
        
        workbook = load_workbook(filename=file_name)
        sheet = workbook.active

        if (sheet_name):
            sheet = workbook[sheet_name]

        if (cell):
            sheet[cell] = value

        workbook.save(file_name)
