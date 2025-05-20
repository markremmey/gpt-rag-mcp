import logging
import time
import aiohttp
import asyncio
import sqlparse

from typing import Annotated, Any, Dict
from semantic_kernel.functions import kernel_function
from semantic_kernel.functions.kernel_plugin import KernelPlugin
from semantic_kernel.agents.chat_completion.chat_completion_agent import ChatCompletionAgent, ChatHistoryAgentThread
from semantic_kernel.agents.agent import AgentResponseItem

from .base_plugin import BasePlugin
from models.types import *

from connectors import AzureOpenAIConnector, CosmosDBClient, SQLDBClient, SQLEndpointClient, SemanticModelConfig, SQLEndpointConfig, SemanticModelClient
from connectors.types import SQLDatabaseConfig

from tools.common.datetools import get_today_date, get_time

class Nl2SqlPlugin(BasePlugin):
    
    def __init__(self, settings : Dict= {}):
        super().__init__(settings)

        self.aoai = AzureOpenAIConnector(self.config)

        self.datasource = settings.get("datasource", "default")
        self.search_index = settings.get('search_index', "nl2sql-tables")

        get_all_datasources_info_tool = KernelPlugin(
            name="get_all_datasources_info",
            description="Get all datasources information.",
            functions=[self.get_all_tables_info]
        )

        get_schema_info_tool = KernelPlugin(
            name="get_schema_info_tool",
            description="Get all datasources information.",
            functions=[self.get_schema_info]
        )

        validate_sql_query_tool = KernelPlugin(
            name="validate_sql_query_tool",
            description="Get all datasources information.",
            functions=[self.validate_sql_query]
        )

        queries_retrieval_tool = KernelPlugin(
            name="queries_retrieval_tool",
            description="Get all datasources information.",
            functions=[self.queries_retrieval]
        )

        get_all_tables_info_tool = KernelPlugin(
            name="get_all_tables_info_tool",
            description="Get all datasources information.",
            functions=[self.get_all_tables_info]
        )

        execute_sql_query_tool = KernelPlugin(
            name="execute_sql_query_tool",
            description="Get all datasources information.",
            functions=[self.execute_sql_query]
        )

        get_today_date_tool = KernelPlugin(
            name="get_today_date",
            description="Get all datasources information.",
            functions=[get_today_date]
        )

        get_time_tool = KernelPlugin(
            name="get_time",
            description="Get all datasources information.",
            functions=[get_time]
        )

        self.agent = ChatCompletionAgent(
            service=self._get_model_client(),
            name="Assistant",
            instructions="You are a SQL expert. You will be provided with a question and you will return the SQL query to answer it.",
            plugins=[get_all_datasources_info_tool, get_schema_info_tool, validate_sql_query_tool, queries_retrieval_tool, get_all_tables_info_tool, execute_sql_query_tool, get_today_date_tool, get_time_tool],

        )

    @kernel_function(
        name="search_sql",
        description="Used to search a SQL database.",
    )
    async def execute(
        self, 
        query: Annotated[str, "The user search query."]
        ) -> Any:
        """
        Do a basic search query.
        """

        try:
            full_message = ''
            result = self.agent.invoke(messages=query)
            async for response in result:
                if isinstance(response, ChatHistoryAgentThread):
                    # Process the response as needed
                    pass
                elif isinstance(response, AgentResponseItem):
                    full_message += response.message.content
                else:
                    # Handle other types of responses
                    pass

            return full_message
            
        except Exception as e:
            logging.error(f"[nl2sql] Error executing search query: {e}")
            return f"Error executing search query: {e}"

    async def _perform_search(self, body: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a search query against the specified Azure AI Search index.

        Args:
            body (dict): The JSON body for the search request.
            search_index (str): The name of the search index to query.

        Returns:
            dict: The JSON response from the search service.

        Raises:
            Exception: If the search query fails or an error occurs obtaining the token.
        """
        search_service = self.config.get_value("AZURE_SEARCH_SERVICE")
        if not search_service:
            raise Exception("AZURE_SEARCH_SERVICE environment variable is not set.")
        search_api_version = self.config.get_value("AZURE_SEARCH_API_VERSION", "2024-07-01")

        # Build the search endpoint URL.
        search_endpoint = (
            f"https://{search_service}.search.windows.net/indexes/{self.search_index}/docs/search"
            f"?api-version={search_api_version}"
        )

        # Obtain an access token for the search service.
        try:
            azure_search_scope = "https://search.azure.com/.default"
            token = self.config.credential.get_token(azure_search_scope).token
        except Exception as e:
            logging.error("Error obtaining Azure Search token.", exc_info=True)
            raise Exception("Failed to obtain Azure Search token.") from e

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        # Perform the asynchronous HTTP POST request.
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(search_endpoint, headers=headers, json=body) as response:
                    if response.status >= 400:
                        text = await response.text()
                        error_message = f"Status code: {response.status}. Error: {text}"
                        logging.error(f"[tables] {error_message}")
                        raise Exception(error_message)
                    result = await response.json()
                    return result
            except Exception as e:
                logging.error("Error during the search HTTP request.", exc_info=True)
                raise Exception("Failed to execute search query.") from e

    @kernel_function(
        name="get_all_tables_info",
        description="Retrieve a list of tables filtering by the given datasource.",
    )
    async def get_all_tables_info(
        self
    ) -> TablesList:
        """
        Retrieve a list of tables filtering by the given datasource.
        Each entry will have "table", "description", and "datasource".

        Returns:
            TablesList: Contains a list of TableItem objects and an optional error message.
        """
        safe_datasource = self.datasource.replace("'", "''")
        filter_expression = f"datasource eq '{safe_datasource}'"

        body = {
            "search": "*",
            "filter": filter_expression,
            "select": "table, description, datasource",
            "top": 1000  # Adjust based on your expected document count.
        }

        logging.info(f"[tables] Querying Azure AI Search for tables in datasource '{self.datasource}'")
        tables_info: List[TableItem] = []
        error_message: Optional[str] = None

        try:
            start_time = time.time()
            result = await self._perform_search(body)
            elapsed = round(time.time() - start_time, 2)
            logging.info(f"[tables] Finished querying tables in {elapsed} seconds")

            for doc in result.get("value", []):
                table_item = TableItem(
                    table=doc.get("table", ""),
                    description=doc.get("description", ""),
                    datasource=doc.get("datasource", "")
                )
                tables_info.append(table_item)
        except Exception as e:
            error_message = str(e)
            logging.error(f"[tables] Error querying tables: {error_message}")

        if not tables_info:
            return TablesList(
                tables=[],
                error=f"No datasource with name '{self.datasource}' was found. {error_message or ''}".strip()
            )

        return TablesList(tables=tables_info, error=error_message)


    @kernel_function(
        name="get_schema_info",
        description="Retrieve information about tables and columns from the data dictionary.",
    )
    # -----------------------------------------------------------------------------
    # Function to retrieve schema information for a given table from the index
    # -----------------------------------------------------------------------------
    async def get_schema_info(
        self,
        table_name: Annotated[str, "Target table"]
    ) -> SchemaInfo:
        """
        Retrieve schema information for a specific table in a given datasource.
        Returns the table's description and its columns.

        Returns:
            SchemaInfo: Contains the schema details or an error message.
        """
        safe_datasource = self.datasource.replace("'", "''")
        safe_table_name = table_name.replace("'", "''")
        filter_expression = f"datasource eq '{safe_datasource}' and table eq '{safe_table_name}'"

        body = {
            "search": "*",
            "filter": filter_expression,
            "select": "table, description, datasource, columns",
            "top": 1
        }

        logging.info(f"[tables] Querying Azure AI Search for schema info for table '{table_name}' in datasource '{self.datasource}'")
        error_message: Optional[str] = None

        try:
            start_time = time.time()
            result = await self._perform_search(body)
            elapsed = round(time.time() - start_time, 2)
            logging.info(f"[tables] Finished querying schema info in {elapsed} seconds")

            docs = result.get("value", [])
            if not docs:
                error_message = f"Table '{table_name}' not found in datasource '{self.datasource}'."
                return SchemaInfo(
                    datasource=self.datasource,
                    table=table_name,
                    error=error_message,
                    columns=None
                )

            doc = docs[0]
            columns_data = doc.get("columns", [])
            columns: Dict[str, str] = {}
            if isinstance(columns_data, list):
                for col in columns_data:
                    col_name = col.get("name")
                    col_description = col.get("description", "")
                    if col_name:
                        columns[col_name] = col_description

            return SchemaInfo(
                datasource=self.datasource,
                table=doc.get("table", table_name),
                description=doc.get("description", ""),
                columns=columns
            )
        except Exception as e:
            error_message = str(e)
            logging.error(f"[tables] Error querying schema info: {error_message}")
            return SchemaInfo(
                datasource=self.datasource,
                table=table_name,
                error=error_message,
                columns=None
            )


    @kernel_function(
        name="tables_retrieval",
        description="Retrieve necessary tables from the retrieval system based on an optimized input query.",
    )
    # ---------------------------------------------------------------------------
    # Function to retrieve necessary tables from the retrieval system
    # based on an optimized input query, to construct a response to the user's request.
    # ---------------------------------------------------------------------------
    async def tables_retrieval(
        self,
        input: Annotated[str, "A query string optimized to retrieve necessary tables from the retrieval system to construct a response"]
    ) -> TablesRetrievalResult:
        """
        Retrieves necessary tables from the retrieval system based on the input query.

        Returns:
            TablesRetrievalResult: An object containing a list of TableRetrievalItem objects.
                                If an error occurs, the 'error' field is populated.
        """
        # Read search configuration from environment variables.
        search_approach = self.config.get_value("AZURE_SEARCH_APPROACH", "hybrid")
        search_top_k = 10
        use_semantic = self.config.get_value("AZURE_SEARCH_USE_SEMANTIC", "false").lower() == "true"
        semantic_search_config = self.config.get_value("AZURE_SEARCH_SEMANTIC_SEARCH_CONFIG", "my-semantic-config")

        search_query = input  # The optimized query string.
        search_results: List[TableRetrievalItem] = []
        error_message: Optional[str] = None

        try:
            # Generate embeddings for the search query using the Azure OpenAI Client.
            logging.info(f"[tables] Generating question embeddings. Search query: {search_query}")
            embeddings_query = await asyncio.to_thread(self.aoai.get_embeddings, search_query)
            logging.info("[tables] Finished generating question embeddings.")

            # Prepare the request body.
            body: Dict[str, Any] = {
                "select": "table, description",
                "top": search_top_k
            }
            # Apply datasource filter if provided.
            if self.datasource:
                body["filter"] = f"datasource eq '{self.datasource}'"

            # Adjust the body based on the search approach.
            if search_approach.lower() == "term":
                body["search"] = search_query
            elif search_approach.lower() == "vector":
                body["vectorQueries"] = [{
                    "kind": "vector",
                    "vector": embeddings_query,
                    "fields": "contentVector",
                    "k": int(search_top_k)
                }]
            elif search_approach.lower() == "hybrid":
                body["search"] = search_query
                body["vectorQueries"] = [{
                    "kind": "vector",
                    "vector": embeddings_query,
                    "fields": "contentVector",
                    "k": int(search_top_k)
                }]

            # If semantic search is enabled and we're not using vector-only search.
            if use_semantic and search_approach.lower() != "vector":
                body["queryType"] = "semantic"
                body["semanticConfiguration"] = semantic_search_config

            logging.info(f"[tables] Querying Azure AI Search for tables. Search query: {search_query}")
            start_time = time.time()
            result = await self._perform_search(body)
            elapsed = round(time.time() - start_time, 2)
            logging.info(f"[tables] Finished querying Azure AI Search in {elapsed} seconds")

            # Process the returned documents.
            if result.get("value"):
                logging.info(f"[tables] {len(result['value'])} documents retrieved")
                for doc in result["value"]:
                    table_name = doc.get("table", "")
                    description = doc.get("description", "")
                    search_results.append(TableRetrievalItem(
                        table=table_name,
                        description=description,
                        datasource=self.datasource
                    ))
            else:
                logging.info("[tables] No documents retrieved")
        except Exception as e:
            error_message = str(e)
            logging.error(f"[tables] Error when retrieving tables: {error_message}")

        return TablesRetrievalResult(tables=search_results, error=error_message)

    @kernel_function(
        name="validate_sql_query",
        description="Validate the syntax of an SQL query.",
    )
    def validate_sql_query(query: Annotated[str, "SQL Query"]) -> ValidateSQLQueryResult:
        """
        Validate the syntax of an SQL query.
        Returns a ValidateSQLQueryResult indicating validity.
        """
        try:
            parsed = sqlparse.parse(query)
            if parsed and len(parsed) > 0:
                return ValidateSQLQueryResult(is_valid=True)
            else:
                return ValidateSQLQueryResult(is_valid=False, error="Query could not be parsed.")
        except Exception as e:
            return ValidateSQLQueryResult(is_valid=False, error=str(e))

    @kernel_function(
        name="execute_dax_query",
        description="Validate the syntax of an SQL query.",
    )
    async def execute_dax_query(
        self,
        datasource: Annotated[str, "Target datasource"], 
        query: Annotated[str, "DAX Query"], 
        access_token: Annotated[str, "User Access Token"]) -> ExecuteQueryResult:
        """
        Execute a DAX query against a semantic model datasource and return the results.
        """
        try:
            cosmosdb = CosmosDBClient()
            datasources_container = self.config.get_value('DATASOURCES_CONTAINER', 'datasources')
            datasource_config = await cosmosdb.get_document(datasources_container, datasource)
            if not datasource_config or datasource_config.get("type") != "semantic_model":
                return ExecuteQueryResult(error=f"{datasource} datasource configuration not found or invalid for Semantic Model.")
        
            semantic_model_config = SemanticModelConfig(
                id=datasource_config.get("id"),
                description=datasource_config.get("description"),
                type=datasource_config.get("type"),
                organization=datasource_config.get("organization"),
                dataset=datasource_config.get("dataset"),
                workspace=datasource_config.get("workspace"),
                tenant_id=datasource_config.get("tenant_id"),
                client_id=datasource_config.get("client_id")
            ) 
            semantic_client = SemanticModelClient(semantic_model_config)
            results = await semantic_client.execute_restapi_dax_query(dax_query=query, user_token=access_token)
            return ExecuteQueryResult(results=results)
        except Exception as e:
            return ExecuteQueryResult(error=str(e))

    @kernel_function(
        name="execute_sql_query",
        description="Execute an SQL query and return the results.",
    )
    async def execute_sql_query(
        self,
        query: Annotated[str, "SQL Query"]
    ) -> ExecuteQueryResult:
        """
        Execute a SQL query against a SQL datasource and return the results.
        Supports both 'sql_endpoint' and 'sql_database' types.
        Only SELECT statements are allowed.
        """
        try:
            # Fetch the datasource configuration
            cosmosdb = CosmosDBClient()
            datasources_container = self.config.get_value('DATASOURCES_CONTAINER', 'datasources')
            datasource_config = await cosmosdb.get_document(datasources_container, self.datasource)

            if not datasource_config:
                return ExecuteQueryResult(error=f"{self.datasource} datasource configuration not found.")

            # Determine datasource type and initialize the appropriate client
            datasource_type = datasource_config.get("type")
            
            if datasource_type == "sql_endpoint":
                sql_endpoint_config = SQLEndpointConfig(
                    id=datasource_config.get("id"),
                    description=datasource_config.get("description"),
                    type=datasource_config.get("type"),
                    organization=datasource_config.get("organization"),
                    server=datasource_config.get("server"),
                    database=datasource_config.get("database"),
                    tenant_id=datasource_config.get("tenant_id"),
                    client_id=datasource_config.get("client_id")
                )
                sql_client = SQLEndpointClient(sql_endpoint_config)

            elif datasource_type == "sql_database":
                sql_database_config = SQLDatabaseConfig(
                    id=datasource_config.get("id"),
                    description=datasource_config.get("description"),
                    type=datasource_config.get("type"),
                    server=datasource_config.get("server"),
                    database=datasource_config.get("database"),
                    uid=datasource_config.get("uid", None)
                )
                sql_client = SQLDBClient(sql_database_config)

            else:
                return ExecuteQueryResult(error="Datasource type not supported for SQL queries.")

            # Create a connection and execute the query
            connection = await sql_client.create_connection()
            cursor = connection.cursor()

            # Validate that only SELECT statements are allowed
            if not query.strip().lower().startswith('select'):
                return ExecuteQueryResult(error="Only SELECT statements are allowed.")

            cursor.execute(query)
            
            # Fetch and structure the results
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            results = [dict(zip(columns, row)) for row in rows]

            return ExecuteQueryResult(results=results)

        except Exception as e:
            # Handle any exceptions and return the error
            return ExecuteQueryResult(error=str(e))
        
    @kernel_function(
        name="queries_retrieval",
        description="Retrieve query details from the search system based on the user's input.",
    )
    async def queries_retrieval(
        self,
        input: Annotated[str, "The user ask"],
        datasource: Annotated[Optional[str], "Target datasource name"] = None,
    ) -> QueriesRetrievalResult:
        """
        Retrieves query details from the search system based on the user's input.
        This async version uses aiohttp for non-blocking HTTP calls.
        
        Args:
            input (str): The user question.
            datasource (Optional[str]): The target datasource name.
            
        Returns:
            QueriesRetrievalResult: A model containing search results where each result includes
                                    question, query and reasoning.
                                    If an error occurs, the 'error' field is populated.
        """
        aoai = AzureOpenAIConnector(self.config)

        # Define search approaches
        VECTOR_SEARCH_APPROACH = 'vector'
        TERM_SEARCH_APPROACH = 'term'
        HYBRID_SEARCH_APPROACH = 'hybrid'

        # Read configuration from environment variables
        search_index = self.config.get_value('NL2SQL_QUERIES_INDEX', 'nl2sql-queries')
        search_approach = self.config.get_value('AZURE_SEARCH_APPROACH', HYBRID_SEARCH_APPROACH)
        search_top_k = 3

        use_semantic = self.config.get_value('AZURE_SEARCH_USE_SEMANTIC', "false").lower() == "true"
        semantic_search_config = self.config.get_value('AZURE_SEARCH_SEMANTIC_SEARCH_CONFIG', 'my-semantic-config')
        search_service = self.config.get_value('AZURE_SEARCH_SERVICE')
        search_api_version = self.config.get_value('AZURE_SEARCH_API_VERSION', '2024-07-01')

        search_results = []
        search_query = input
        error_message = None

        try:
            # Create the credential to obtain a token for Azure Search.
            # Generate embeddings asynchronously (using a thread if the SDK is blocking).
            start_time = time.time()
            logging.info(f"[queries_retrieval] Generating question embeddings. Search query: {search_query}")
            embeddings_query = await asyncio.to_thread(aoai.get_embeddings, search_query)
            response_time = round(time.time() - start_time, 2)
            logging.info(f"[queries_retrieval] Finished generating question embeddings in {response_time} seconds")

            # Obtain the Azure Search token asynchronously.
            token_response = await asyncio.to_thread(config.credential.get_token, "https://search.azure.com/.default")
            azure_search_key = token_response.token

            # Prepare the request body for the search query.
            body = {
                "select": "question, query, reasoning",
                "top": search_top_k
            }
            if datasource:
                safe_datasource = datasource.replace("'", "''")
                body["filter"] = f"datasource eq '{safe_datasource}'"

            # Choose the search approach.
            if search_approach == TERM_SEARCH_APPROACH:
                body["search"] = search_query
            elif search_approach == VECTOR_SEARCH_APPROACH:
                body["vectorQueries"] = [{
                    "kind": "vector",
                    "vector": embeddings_query,
                    "fields": "contentVector",
                    "k": int(search_top_k)
                }]
            elif search_approach == HYBRID_SEARCH_APPROACH:
                body["search"] = search_query
                body["vectorQueries"] = [{
                    "kind": "vector",
                    "vector": embeddings_query,
                    "fields": "contentVector",
                    "k": int(search_top_k)
                }]

            # If semantic search is enabled and we're not in pure vector mode, add semantic parameters.
            if use_semantic and search_approach != VECTOR_SEARCH_APPROACH:
                body["queryType"] = "semantic"
                body["semanticConfiguration"] = semantic_search_config

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {azure_search_key}'
            }

            search_endpoint = (
                f"https://{search_service}.search.windows.net/indexes/{search_index}/docs/search"
                f"?api-version={search_api_version}"
            )

            logging.info(f"[queries_retrieval] Querying Azure AI Search. Search query: {search_query}")
            start_time = time.time()

            # Use aiohttp to make the asynchronous POST call.
            async with aiohttp.ClientSession() as session:
                async with session.post(search_endpoint, headers=headers, json=body) as response:
                    if response.status >= 400:
                        text = await response.text()
                        error_message = f"Status code: {response.status}. Error: {text if text else 'Unknown error'}."
                        logging.error(f"[queries_retrieval] {error_message}")
                    else:
                        json_response = await response.json()
                        if json_response.get('value'):
                            logging.info(f"[queries_retrieval] {len(json_response['value'])} documents retrieved")
                            for doc in json_response['value']:
                                question = doc.get('question', '')
                                query = doc.get('query', '')
                                reasoning = doc.get('reasoning', '')
                                search_results.append({
                                    "question": question,
                                    "query": query,
                                    "reasoning": reasoning
                                })
                        else:
                            logging.info("[queries_retrieval] No documents retrieved")

            response_time = round(time.time() - start_time, 2)
            logging.info(f"[queries_retrieval] Finished querying Azure AI Search in {response_time} seconds")

        except Exception as e:
            error_message = str(e)
            logging.error(f"[queries_retrieval] Error when getting the answer: {error_message}")

        # Convert the list of dictionaries into a list of QueryItem instances.
        query_items = [QueryItem(**result) for result in search_results]

        return QueriesRetrievalResult(queries=query_items, error=error_message)
