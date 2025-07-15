import sys
import logging
import asyncio

from typing import Dict
from semantic_kernel.functions import kernel_function
from configuration import Configuration

from ..base_plugin import BasePlugin
from connectors import AzureOpenAIConnector

import graphrag.api as api
from graphrag.config.models.graph_rag_config import GraphRagConfig
from graphrag.logger.base import ProgressLogger
from graphrag.logger.factory import LoggerFactory, LoggerType
from graphrag.config.enums import CacheType, IndexingMethod
from graphrag.storage.pipeline_storage import PipelineStorage
from graphrag.config.load_config import load_config
from graphrag.config.logging import enable_logging_with_config
from graphrag.index.validate_config import validate_config_names
from graphrag.logger.base import ProgressLogger
from graphrag.utils.cli import redact

log = logging.getLogger(__name__)

def _logger(logger: ProgressLogger):
        def info(msg: str, verbose: bool = False):
            log.info(msg)
            if verbose:
                logger.info(msg)

        def error(msg: str, verbose: bool = False):
            log.error(msg)
            if verbose:
                logger.error(msg)

        def success(msg: str, verbose: bool = False):
            log.info(msg)
            if verbose:
                logger.success(msg)

        return info, error, success

def _register_signal_handlers(logger: ProgressLogger):
    import signal

    def handle_signal(signum, _):
        # Handle the signal here
        logger.info(f"Received signal {signum}, exiting...")  # noqa: G004
        logger.dispose()
        for task in asyncio.all_tasks():
            task.cancel()
        logger.info("All tasks cancelled. Exiting...")

    # Register signal handlers for SIGINT and SIGHUP
    signal.signal(signal.SIGINT, handle_signal)

    if sys.platform != "win32":
        signal.signal(signal.SIGHUP, handle_signal)

class GraphRagPlugin(BasePlugin):
    def __init__(self, settings : Dict= {}):

        super().__init__(settings)

        self.aoai : AzureOpenAIConnector = AzureOpenAIConnector(self.config)

        self.graph_config = GraphRagConfig()

        #modify the graph config with the settings
        input_storage : PipelineStorage = self.graph_config.input.storage
        input_storage.type = self.config.get("input_storage_type", "blob")
        input_storage.connection_string = self.config.get("input_storage_connection_string", None)
        input_storage.container_name = self.config.get("input_storage_container_name", "graphrag")
        input_storage.blob_prefix = self.config.get("input_storage_blob_prefix", "input/")
        input_storage.blob_suffix = self.config.get("input_storage_blob_suffix", ".json")

        output_storage : PipelineStorage = self.graph_config.output.storage
        output_storage.type = self.config.get("output_storage_type", "blob")
        output_storage.connection_string = self.config.get("output_storage_connection_string", None)
        output_storage.container_name = self.config.get("output_storage_container_name", "graphrag")
        output_storage.blob_prefix = self.config.get("output_storage_blob_prefix", "output/")
        output_storage.blob_suffix = self.config.get("output_storage_blob_suffix", ".json")

        cache_storage : PipelineStorage = self.graph_config.cache.storage
        cache_storage.type = self.config.get("cache_storage_type", "blob")
        cache_storage.connection_string = self.config.get("cache_storage_connection_string", None)
        cache_storage.container_name = self.config.get("cache_storage_container_name", "graphrag")
        cache_storage.blob_prefix = self.config.get("cache_storage_blob_prefix", "cache/")
        cache_storage.blob_suffix = self.config.get("cache_storage_blob_suffix", ".json")
        

    def _run_index(
        config : GraphRagConfig,
        method,
        is_update_run,
        verbose,
        memprofile,
        cache,
        logger,
        dry_run,
        skip_validation,
    ):
        progress_logger = LoggerFactory().create_logger(logger)
        info, error, success = _logger(progress_logger)

        if not cache:
            config.cache.type = CacheType.none

        enabled_logging, log_path = enable_logging_with_config(config, verbose)
        if enabled_logging:
            info(f"Logging enabled at {log_path}", True)
        else:
            info(
                f"Logging not enabled for config {redact(config.model_dump())}",
                True,
            )

        if not skip_validation:
            validate_config_names(progress_logger, config)

        info(f"Starting pipeline run. {dry_run=}", verbose)
        info(
            f"Using default configuration: {redact(config.model_dump())}",
            verbose,
        )

        if dry_run:
            info("Dry run complete, exiting...", True)
            return

        _register_signal_handlers(progress_logger)

        outputs = asyncio.run(
            api.build_index(
                config=config,
                method=method,
                is_update_run=is_update_run,
                memory_profile=memprofile,
                progress_logger=progress_logger,
            )
        )
        encountered_errors = any(
            output.errors and len(output.errors) > 0 for output in outputs
        )

        progress_logger.stop()
        if encountered_errors:
            error(
                "Errors occurred during the pipeline run, see logs for more details.", True
            )
        else:
            success("All workflows completed successfully.", True)

        return

    @kernel_function(
        name="run_graph_query",
        description="Runs a graph query with the given prompt.",
    )
    def search(self, 
        user_prompt: str):
        """
        Runs a graph query with the given prompt.
        """

        _get_user_context = self._get_user_context()

        pass

    @kernel_function(
        name="index_document_uri",
        description="Index a document via uri and add to graph.",
    )
    def index_document(self, 
        documentUri: str):
        """
        Runs a graph query with the given prompt.
        """

        _get_user_context = self._get_user_context()

        method = IndexingMethod.Standard
        verbose = False
        memprofile = False
        cache = True
        logger = LoggerType.RICH
        dry_run = False
        skip_validation = False

        self._run_index(
            config=self.graph_config,
            method=method,
            is_update_run=False,
            verbose=verbose,
            memprofile=memprofile,
            cache=cache,
            logger=logger,
            dry_run=dry_run,
            skip_validation=skip_validation,
        )

    @kernel_function(
        name="index_document_content",
        description="Index a document content and add to graph.",
    )
    def index_document_content(self, 
        content: str):
        """
        Index document content and add to graph.
        """

        _get_user_context = self._get_user_context()

        pass

    @kernel_function(
        name="add_graph_node",
        description="Adds a new node to the graph with the given prompt.",
    )
    def add_node(self, 
        user_prompt: str):
        """
        Adds a new node to the graph with the given prompt.
        """

        _get_user_context = self._get_user_context()

        pass

    @kernel_function(
        name="add_graph_edge",
        description="Adds a new edge to the graph with the given prompt.",
    )
    def add_edge(self, 
        user_prompt: str):
        """
        Adds a new edge to the graph with the given prompt.
        """

        _get_user_context = self._get_user_context()

        pass

    @kernel_function(
        name="get_graph_nodes",
        description="Returns all nodes in the graph.",
    )   
    def get_nodes(self):
        """
        Returns all nodes in the graph.
        """

        _get_user_context = self._get_user_context()

        pass

    @kernel_function(
        name="get_graph_edges",
        description="Returns all edges in the graph.",
    )

    def get_edges(self):
        """
        Returns all edges in the graph.
        """

        _get_user_context = self._get_user_context()

        pass

    @kernel_function(
        name="get_graph_node",
        description="Returns a node in the graph with the given ID.",
    )
    def get_node(self, 
        node_id: str):
        """
        Returns a node in the graph with the given ID.
        """

        _get_user_context = self._get_user_context()

        pass

    @kernel_function(
        name="get_graph_edge",
        description="Returns an edge in the graph with the given ID.",
    )
    def get_edge(self, 
        edge_id: str):
        """
        Returns an edge in the graph with the given ID.
        """

        _get_user_context = self._get_user_context()

        pass