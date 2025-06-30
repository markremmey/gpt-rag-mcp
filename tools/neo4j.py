from neo4j import GraphDatabase
from neo4j_graphrag.indexes import create_vector_index
from neo4j_graphrag.embeddings.openai import OpenAIEmbeddings
from neo4j_graphrag.retrievers import VectorRetriever

from typing import Dict
from semantic_kernel.functions import kernel_function
from configuration import Configuration
from tools.graphrag.graphrag import GraphRagPlugin

from connectors import AzureOpenAIConnector

class Neo4jPlugin(GraphRagPlugin):
    def __init__(self, settings : Dict= {}):

        super().__init__(settings)

        self.aoai : AzureOpenAIConnector = AzureOpenAIConnector(self.config)

        self.uri = self.settings.get("neo4j_uri", "neo4j://localhost:7687")
        self.auth = (self.settings.get("neo4j_user", "neo4j"), self.settings.get("neo4j_password", "password"))
        self.index_name = self.settings.get("neo4j_index_name", "vector-index-name")
        self.label = self.settings.get("neo4j_label", "Document")
        self.embedding_model = self.settings.get("neo4j_embedding_model", "text-embedding-3-large")
        self.embedding_property = self.settings.get("neo4j_embedding_property", "vectorProperty")
        self.similarity_fn = self.settings.get("neo4j_similarity_fn", "euclidean")

        # Connect to Neo4j database
        self.driver = GraphDatabase.driver(self.uri, auth=self.auth)

        # Creating the index
        create_vector_index(
            self.driver,
            self.index_name,
            label=self.label,
            embedding_property=self.embedding_property,
            dimensions=1536,
            similarity_fn=self.similarity_fn,
        )

    @kernel_function(
        name="run_graph_query",
        description="Runs a graph query with the given prompt.",
    )
    def search(self, 
        query_text: str):
        """
        Runs a graph query with the given prompt.
        """

        _get_user_context = self._get_user_context()

        # Create Embedder object
        embedder = OpenAIEmbeddings(model=self.embedding_model)

        # Initialize the retriever
        retriever = VectorRetriever(self.driver, self.index_name, embedder)

        # Run the similarity search
        response = retriever.search(query_text=query_text, top_k=5)
        return response