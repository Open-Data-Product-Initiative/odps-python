"""MCP (Model Context Protocol) surface for the Open Data Products SDK.

Modules:
- ``tools``: pure data registry of tool definitions + handlers
- ``manifest``: ARWS-style agent manifest generator
- ``server``: stdio JSON-RPC 2.0 MCP server bootstrap
"""

from .manifest import generate_agent_manifest
from .tools import TOOLS, get_tool

__all__ = ["TOOLS", "generate_agent_manifest", "get_tool"]
