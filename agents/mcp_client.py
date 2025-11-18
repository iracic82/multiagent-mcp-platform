"""
MCP Client for connecting to multiple MCP servers
Supports both HTTP (spec-compliant) and SSE (deprecated, fallback) transports
"""

import asyncio
import json
import logging
import sys
from typing import Any, Dict, List, Optional
from contextlib import AsyncExitStack
from mcp import ClientSession
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamablehttp_client
import httpx

# Configure logging - write to stderr only
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)


class MCPClient:
    """Client for connecting to and calling multiple MCP servers"""

    def __init__(self):
        self.servers: Dict[str, Dict[str, Any]] = {}
        self.sessions: Dict[str, ClientSession] = {}
        self.available_tools: Dict[str, List[Dict[str, Any]]] = {}
        self.exit_stacks: Dict[str, AsyncExitStack] = {}  # Store exit stacks for cleanup

    async def connect_server(
        self,
        server_name: str,
        url: str
    ):
        """
        Connect to an MCP server with HTTP-first, SSE-fallback strategy.

        Tries HTTP transport first (spec-compliant), falls back to SSE (deprecated) if HTTP fails.
        Automatically converts URLs:
        - http://host:port/sse -> http://host:port/mcp (for HTTP attempt)
        - http://host:port/mcp -> uses as-is (for HTTP attempt)

        Args:
            server_name: Unique name for this server
            url: URL of the MCP server
                 (e.g., 'http://localhost:3001/sse' or 'http://localhost:4001/mcp')
        """
        if server_name in self.sessions:
            logger.info(f"Already connected to {server_name}")
            return

        # Determine HTTP and SSE URLs
        # HTTP servers: 4001-4004/mcp
        # SSE servers:  3001-3004/sse
        if "/sse" in url:
            # Old SSE URL -> convert to HTTP
            http_url = url.replace("/sse", "/mcp").replace(":3001", ":4001").replace(":3002", ":4002").replace(":3003", ":4003").replace(":3004", ":4004")
            sse_url = url
        elif "/mcp" in url:
            # New HTTP URL -> convert back to SSE for fallback
            http_url = url
            sse_url = url.replace("/mcp", "/sse").replace(":4001", ":3001").replace(":4002", ":3002").replace(":4003", ":3003").replace(":4004", ":3004")
        else:
            # No path specified -> add both
            base_url = url.rstrip("/")
            http_url = f"{base_url}/mcp"
            sse_url = f"{base_url}/sse"

        # Try HTTP first (spec-compliant)
        try:
            logger.info(f"Attempting HTTP connection to {server_name} at {http_url}")
            await self._connect_http(server_name, http_url)
            logger.info(f"✅ Connected to {server_name} via HTTP (spec-compliant)")
            return
        except Exception as http_error:
            logger.warning(f"HTTP connection failed for {server_name}: {http_error}")
            logger.info(f"Falling back to SSE transport for {server_name}")

        # Fallback to SSE (deprecated but working)
        try:
            logger.info(f"Attempting SSE connection to {server_name} at {sse_url}")
            await self._connect_sse(server_name, sse_url)
            logger.info(f"⚠️  Connected to {server_name} via SSE (deprecated, fallback mode)")
        except Exception as sse_error:
            logger.error(f"Both HTTP and SSE connections failed for {server_name}")
            logger.error(f"  HTTP error: {http_error}")
            logger.error(f"  SSE error: {sse_error}")
            raise Exception(f"Failed to connect to {server_name} via both HTTP and SSE transports")

    async def _connect_http(self, server_name: str, url: str):
        """Connect to MCP server via HTTP transport (spec-compliant streamable HTTP)"""
        # Create exit stack for proper cleanup
        exit_stack = AsyncExitStack()
        self.exit_stacks[server_name] = exit_stack

        try:
            # Use official MCP streamable HTTP client
            # Returns tuple of (read_stream, write_stream, get_session_id)
            streams = await exit_stack.enter_async_context(
                streamablehttp_client(
                    url=url,
                    timeout=30.0,  # Explicit float for HTTP operations
                    sse_read_timeout=300.0  # Explicit float for SSE read operations
                )
            )

            # Unpack the tuple - ClientSession only needs first 2 items
            read_stream, write_stream, get_session_id = streams

            # Create session with read and write streams only
            session = await exit_stack.enter_async_context(
                ClientSession(read_stream, write_stream)
            )

            # Initialize session
            await session.initialize()

            # Store session and session ID callback
            self.sessions[server_name] = session
            self.servers[server_name] = {
                "url": url,
                "transport": "http",
                "get_session_id": get_session_id
            }

            # Get available tools
            response = await session.list_tools()
            self.available_tools[server_name] = [
                {
                    "name": tool.name,
                    "description": tool.description or "",
                    "input_schema": tool.inputSchema or {},
                    "server": server_name
                }
                for tool in response.tools
            ]

            logger.info(f"✅ HTTP connection established to {server_name}, available tools: {len(self.available_tools[server_name])}")

        except Exception as e:
            logger.error(f"❌ HTTP connection failed: {e}")
            raise

    async def _connect_sse(self, server_name: str, url: str):
        """Connect to MCP server via SSE transport (deprecated, fallback)"""
        # Create exit stack for proper cleanup
        exit_stack = AsyncExitStack()
        self.exit_stacks[server_name] = exit_stack

        # Connect via SSE
        streams = await exit_stack.enter_async_context(
            sse_client(url=url)
        )

        # Create session
        session = await exit_stack.enter_async_context(
            ClientSession(*streams)
        )

        # Initialize session
        await session.initialize()

        # Store session
        self.sessions[server_name] = session
        self.servers[server_name] = {"url": url, "transport": "sse"}

        # Get available tools
        response = await session.list_tools()
        self.available_tools[server_name] = [
            {
                "name": tool.name,
                "description": tool.description or "",
                "input_schema": tool.inputSchema or {},
                "server": server_name
            }
            for tool in response.tools
        ]

        logger.info(f"Connected to MCP server: {server_name} ({url}), available tools: {len(self.available_tools[server_name])}")

    async def disconnect_server(self, server_name: str):
        """Disconnect from an MCP server"""
        if server_name in self.exit_stacks:
            try:
                await self.exit_stacks[server_name].aclose()
            except Exception as e:
                logger.error(f"Error closing connection to {server_name}: {e}")

            del self.exit_stacks[server_name]

        if server_name in self.sessions:
            del self.sessions[server_name]
        if server_name in self.servers:
            del self.servers[server_name]
        if server_name in self.available_tools:
            del self.available_tools[server_name]

        logger.info(f"Disconnected from {server_name}")

    async def call_tool(
        self,
        server_name: str,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Any:
        """
        Call a tool on a specific MCP server via SSE.

        Args:
            server_name: Name of the server to call
            tool_name: Name of the tool to call
            arguments: Arguments for the tool

        Returns:
            Tool execution result
        """
        if server_name not in self.sessions:
            raise ValueError(f"Not connected to server: {server_name}")

        session = self.sessions[server_name]

        try:
            result = await session.call_tool(tool_name, arguments=arguments)

            # Extract text content from result
            if hasattr(result, 'content') and result.content:
                content_parts = []
                for content in result.content:
                    if hasattr(content, 'text'):
                        content_parts.append(content.text)
                return "\n".join(content_parts) if content_parts else str(result)

            return str(result)

        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}

    def get_all_tools(self) -> List[Dict[str, Any]]:
        """Get all available tools from all connected servers"""
        all_tools = []
        for server_name, tools in self.available_tools.items():
            all_tools.extend(tools)
        return all_tools

    def get_tools_for_llm(self) -> List[Dict[str, Any]]:
        """
        Get all tools formatted for LLM tool calling.
        Adds server information to tool names to avoid conflicts.
        """
        llm_tools = []
        for server_name, tools in self.available_tools.items():
            for tool in tools:
                llm_tools.append({
                    "name": f"{server_name}__{tool['name']}",
                    "description": f"[{server_name}] {tool['description']}",
                    "input_schema": tool["input_schema"]
                })
        return llm_tools

    def parse_tool_call(self, tool_name: str) -> tuple[str, str]:
        """
        Parse a tool name from LLM into server_name and tool_name.

        Args:
            tool_name: Tool name in format "server__tool"

        Returns:
            Tuple of (server_name, tool_name)
        """
        if "__" in tool_name:
            parts = tool_name.split("__", 1)
            return parts[0], parts[1]
        # If no server prefix, try to find the tool
        for server_name, tools in self.available_tools.items():
            for tool in tools:
                if tool["name"] == tool_name:
                    return server_name, tool_name
        raise ValueError(f"Tool not found: {tool_name}")

    async def close_all(self):
        """Close all connections"""
        for server_name in list(self.sessions.keys()):
            await self.disconnect_server(server_name)


# Singleton instance
_mcp_client_instance: Optional[MCPClient] = None


def get_mcp_client() -> MCPClient:
    """Get or create the global MCP client instance"""
    global _mcp_client_instance
    if _mcp_client_instance is None:
        _mcp_client_instance = MCPClient()
    return _mcp_client_instance
