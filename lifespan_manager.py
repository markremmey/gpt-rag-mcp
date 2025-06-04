import logging

from aiohttp import ClientSession
from starlette.applications import Starlette
from starlette.types import ASGIApp, Lifespan
from typing import AsyncIterator
from contextlib import asynccontextmanager
from configuration import Configuration

config: Configuration = None
http_client_session: ClientSession = None

@asynccontextmanager
async def lifespan(app: Starlette) -> AsyncIterator[None]:
    """Async context manager for the FastAPI application lifespan."""
    global config
    global http_client_session
    
    # Create the application configuration
    config = Configuration()

    # Create an aiohttp client session
    http_client_session = ClientSession()

    # Create the plugin manager
    #Telemetry.configure_monitoring(config, f'', 'MCP')

    yield
    
    logging.info("Application shutting down...")

    # Perform shutdown actions here
    await http_client_session.close()

async def get_config() -> Configuration:
    """Retrieves the application configuration."""
    return config

async def get_http_client_session() -> ClientSession:
    """Retrieves the aiohttp client session."""
    return http_client_session
