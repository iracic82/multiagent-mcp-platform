"""
MCP Client for connecting to multiple MCP servers
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
from contextlib import AsyncExitStack
from mcp import ClientSession
from mcp.client.sse import sse_client


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
        Connect to an MCP server via SSE.

        Args:
            server_name: Unique name for this server
            url: SSE URL of the MCP server (e.g., 'http://localhost:3000/sse')
        """
        if server_name in self.sessions:
            print(f"Already connected to {server_name}")
            return

        try:
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
            self.servers[server_name] = {"url": url}

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

            print(f"✓ Connected to MCP server: {server_name} ({url})")
            print(f"  Available tools: {len(self.available_tools[server_name])}")

        except Exception as e:
            print(f"✗ Failed to connect to {server_name}: {e}")
            import traceback
            traceback.print_exc()
            raise

    async def disconnect_server(self, server_name: str):
        """Disconnect from an MCP server"""
        if server_name in self.exit_stacks:
            try:
                await self.exit_stacks[server_name].aclose()
            except Exception as e:
                print(f"Error closing connection to {server_name}: {e}")

            del self.exit_stacks[server_name]

        if server_name in self.sessions:
            del self.sessions[server_name]
        if server_name in self.servers:
            del self.servers[server_name]
        if server_name in self.available_tools:
            del self.available_tools[server_name]

        print(f"✓ Disconnected from {server_name}")

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
