from typing import Annotated, Dict
from semantic_kernel.functions import kernel_function

from .base_plugin import BasePlugin

from databricks.sdk.core import Config, oauth_service_principal
from databricks import sql
import os

class DatabricksPlugin(BasePlugin):
    
    def __init__(self, settings : Dict= {}):
        """
        Initialize Databricks Plugin with the provided settings.
        """
        super().__init__(settings)

        self.server_hostname = settings.get("server_hostname", "")

    def credential_provider(self):
        config = Config(
            host          = f"https://{self.server_hostname}",
            client_id     = os.getenv("DATABRICKS_CLIENT_ID"),
            client_secret = os.getenv("DATABRICKS_CLIENT_SECRET"))
        return oauth_service_principal(config)

    def connect(self):
        """
        Connect to Databricks database.
        """
        # Implement the logic to connect to Databricks database
        with sql.connect(server_hostname  = self.server_hostname,
            http_path            = os.getenv("DATABRICKS_HTTP_PATH"),
            credentials_provider = self.credential_provider) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT current_user()")
                result = cursor.fetchone()
                print(f"Connected to Databricks as {result[0]}")
                return connection

    def execute_query(self, 
                      query: str) -> str:
        """
        Execute a SQL query against Databricks database.
        """
        # Implement the logic to execute the SQL query
        connection = self.connect()
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 + 1")
            result = cursor.fetchall()

            for row in result:
                print(row)
    
    def get_metadata(self, table_name: str) -> str:
        """
        Get metadata for a specific table in Databricks.
        """
        # Implement the logic to get metadata for the specified table
        connection = self.connect()

        with connection.cursor() as cursor:
            cursor.columns(schema_name="default", table_name=table_name)
            print(cursor.fetchall())