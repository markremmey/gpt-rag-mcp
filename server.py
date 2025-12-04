# server.py
import contextlib
from contextlib import asynccontextmanager

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

from mcp.server.fastmcp import FastMCP

# ---- MCP server ----
mcp = FastMCP("Demo")

@mcp.tool()
def add(a: int, b: int) -> int:
    return a + b

@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    return f"Hello, {name}!"

@mcp.prompt()
def greet_user(name: str, style: str = "friendly") -> str:
    styles = {
        "friendly": "Please write a warm, friendly greeting",
        "formal": "Please write a formal, professional greeting",
        "casual": "Please write a casual, relaxed greeting",
    }
    return f"{styles.get(style, styles['friendly'])} for someone named {name}."

# ---- Lifespan: start/stop MCP session manager ----
@asynccontextmanager
async def mcp_lifespan(_app):
    async with contextlib.AsyncExitStack() as stack:
        # This is the key bit you were missing:
        await stack.enter_async_context(mcp.session_manager.run())
        yield  # app is live
        # exit stack will shut it down cleanly

# Optional: health endpoint for probes
async def healthz(_req):
    return JSONResponse({"status": "ok"})

# ---- Parent Starlette app with MCP mounted ----
app = Starlette(
    lifespan=mcp_lifespan,  # << wire in the MCP lifespan
    routes=[
        Route("/healthz", endpoint=healthz),
        # Mount at "/" if you want MCP at root; otherwise use "/mcp"
        Mount("/", app=mcp.streamable_http_app()),
        Mount("/mcp", app=mcp.streamable_http_app()),  # alt path
    ],
)
