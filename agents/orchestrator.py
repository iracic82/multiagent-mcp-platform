"""
Agent Orchestrator for managing multiple agents and MCP servers
"""

import asyncio
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv
from agents.base_agent import BaseAgent
from agents.mcp_client import get_mcp_client


class AgentOrchestrator:
    """
    Orchestrates multiple agents and MCP server connections.
    Handles initialization, routing, and cleanup.
    """

    def __init__(self):
        load_dotenv()
        self.agents: Dict[str, BaseAgent] = {}
        self.mcp_client = get_mcp_client()
        self.is_initialized = False

    async def initialize(
        self,
        mcp_servers: Optional[List[Dict[str, any]]] = None,
        agent_configs: Optional[List[Dict[str, any]]] = None
    ):
        """
        Initialize the orchestrator with MCP servers and agents.

        Args:
            mcp_servers: List of MCP server configurations
                Example: [
                    {"name": "subnet", "url": "http://localhost:3000"},
                    {"name": "aws", "url": "http://localhost:3001"}
                ]
            agent_configs: List of agent configurations
                Example: [
                    {"name": "main", "llm_provider": "claude"},
                    {"name": "security", "llm_provider": "openai"}
                ]
        """
        print("🚀 Initializing Agent Orchestrator...")

        # Connect to MCP servers
        if mcp_servers:
            for server_config in mcp_servers:
                try:
                    await self.mcp_client.connect_server(
                        server_name=server_config["name"],
                        url=server_config["url"]
                    )
                except Exception as e:
                    print(f"⚠️  Failed to connect to {server_config['name']}: {e}")

        # Create agents
        if agent_configs:
            for config in agent_configs:
                await self.create_agent(
                    name=config["name"],
                    llm_provider=config.get("llm_provider", "claude"),
                    system_prompt=config.get("system_prompt")
                )
        else:
            # Create default agent
            await self.create_agent("main", "claude")

        self.is_initialized = True
        print("✅ Orchestrator initialized!")
        self._print_status()

    async def create_agent(
        self,
        name: str,
        llm_provider: str = "claude",
        system_prompt: Optional[str] = None
    ) -> BaseAgent:
        """Create and register a new agent"""
        # Get API keys from environment
        if llm_provider == "claude":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            model = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
        elif llm_provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
        else:
            raise ValueError(f"Unknown LLM provider: {llm_provider}")

        if not api_key:
            raise ValueError(f"API key not found for {llm_provider}. Set {llm_provider.upper()}_API_KEY in .env")

        agent = BaseAgent(
            name=name,
            llm_provider=llm_provider,
            api_key=api_key,
            model=model,
            system_prompt=system_prompt
        )

        self.agents[name] = agent

        # Register other agents for delegation
        for other_name, other_agent in self.agents.items():
            if other_name != name:
                agent.register_agent(other_name, other_agent)
                other_agent.register_agent(name, agent)

        print(f"✓ Created agent: {name} ({llm_provider})")
        return agent

    def get_agent(self, name: str = "main") -> Optional[BaseAgent]:
        """Get an agent by name"""
        return self.agents.get(name)

    async def chat(self, message: str, agent_name: str = "main") -> Dict:
        """
        Send a message to a specific agent.

        Args:
            message: The user's message
            agent_name: Name of the agent to use

        Returns:
            Response dictionary
        """
        if not self.is_initialized:
            raise RuntimeError("Orchestrator not initialized. Call initialize() first.")

        agent = self.get_agent(agent_name)
        if not agent:
            return {
                "error": f"Agent not found: {agent_name}",
                "available_agents": list(self.agents.keys())
            }

        return await agent.chat(message)

    def _print_status(self):
        """Print current orchestrator status"""
        print("\n" + "="*60)
        print("ORCHESTRATOR STATUS")
        print("="*60)

        print(f"\n📡 MCP Servers ({len(self.mcp_client.servers)}):")
        for server_name, server_info in self.mcp_client.servers.items():
            tool_count = len(self.mcp_client.available_tools.get(server_name, []))
            print(f"  • {server_name}: {tool_count} tools")

        print(f"\n🤖 Agents ({len(self.agents)}):")
        for agent_name, agent in self.agents.items():
            print(f"  • {agent_name} ({agent.llm_provider})")

        all_tools = self.mcp_client.get_all_tools()
        print(f"\n🔧 Total Tools Available: {len(all_tools)}")

        print("="*60 + "\n")

    def get_status(self) -> Dict:
        """Get orchestrator status as dictionary"""
        return {
            "initialized": self.is_initialized,
            "mcp_servers": {
                name: {
                    "tools": len(self.mcp_client.available_tools.get(name, []))
                }
                for name in self.mcp_client.servers.keys()
            },
            "agents": {
                name: {
                    "llm_provider": agent.llm_provider,
                    "model": agent.model
                }
                for name, agent in self.agents.items()
            },
            "total_tools": len(self.mcp_client.get_all_tools())
        }

    async def cleanup(self):
        """Clean up all connections"""
        print("\n🧹 Cleaning up...")
        await self.mcp_client.close_all()
        self.agents.clear()
        self.is_initialized = False
        print("✅ Cleanup complete")


# Singleton instance
_orchestrator_instance: Optional[AgentOrchestrator] = None


def get_orchestrator() -> AgentOrchestrator:
    """Get or create the global orchestrator instance"""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = AgentOrchestrator()
    return _orchestrator_instance
