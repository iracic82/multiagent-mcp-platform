"""
Example: External Agent Connecting to YOUR MCP Server

This shows how another developer's agent can connect to your subnet MCP server
and use your tools without needing your agent code.
"""

import asyncio
from contextlib import AsyncExitStack
from mcp import ClientSession
from mcp.client.sse import sse_client


class ExternalAgent:
    """
    An external agent (from another developer/company) that wants to use
    YOUR subnet calculation MCP server.
    """

    def __init__(self):
        self.session = None
        self.exit_stack = AsyncExitStack()
        self.tools = []

    async def connect_to_subnet_mcp(self, mcp_url: str):
        """
        Connect to the public subnet MCP server.

        Args:
            mcp_url: URL of the MCP server (e.g., "http://your-domain.com:3000/sse")
        """
        print(f"🔌 Connecting to external MCP server: {mcp_url}")

        # Establish SSE connection
        streams = await self.exit_stack.enter_async_context(
            sse_client(url=mcp_url)
        )

        # Create MCP session
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(*streams)
        )

        # Initialize and discover tools
        await self.session.initialize()
        response = await self.session.list_tools()

        self.tools = response.tools
        print(f"✅ Connected! Found {len(self.tools)} tools:")
        for tool in self.tools:
            print(f"   - {tool.name}: {tool.description}")

    async def calculate_subnet(self, cidr: str):
        """Use the remote subnet calculation tool"""
        print(f"\n🔧 Calling remote tool: calculate_subnet_info({cidr})")

        result = await self.session.call_tool(
            "calculate_subnet_info",
            arguments={"cidr": cidr}
        )

        # Extract result
        if result.content:
            for content in result.content:
                if hasattr(content, 'text'):
                    print(f"📊 Result: {content.text}")
                    return content.text

        return str(result)

    async def validate_cidr(self, cidr: str):
        """Use the remote CIDR validation tool"""
        print(f"\n✅ Calling remote tool: validate_cidr({cidr})")

        result = await self.session.call_tool(
            "validate_cidr",
            arguments={"cidr": cidr}
        )

        if result.content:
            for content in result.content:
                if hasattr(content, 'text'):
                    print(f"📊 Result: {content.text}")
                    return content.text

        return str(result)

    async def cleanup(self):
        """Close connection"""
        await self.exit_stack.aclose()
        print("🔌 Disconnected from MCP server")


async def main():
    """
    Demo: External agent using YOUR MCP server
    """
    print("="*60)
    print("EXTERNAL AGENT CONNECTING TO YOUR MCP SERVER")
    print("="*60)

    agent = ExternalAgent()

    try:
        # Connect to YOUR MCP server (could be public or authenticated)
        await agent.connect_to_subnet_mcp("http://localhost:3000/sse")

        # Use your tools
        await agent.calculate_subnet("10.0.0.0/16")
        await agent.calculate_subnet("192.168.1.0/24")
        await agent.validate_cidr("invalid-cidr")

    finally:
        await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
