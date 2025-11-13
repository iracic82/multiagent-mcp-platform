"""
Agent-to-Agent (A2A) Client Library

Simple library to connect your agent to the agent system.

Example:
    from a2a_client import A2AClient

    # Connect
    client = A2AClient("http://localhost:8000")

    # See what's available
    registry = client.discover()
    print(f"Available: {[a['name'] for a in registry['agents']]}")

    # Send a message
    response = client.chat(
        message="Create subnet 10.0.0.0/24",
        agent="network_specialist"
    )
    print(response['response'])
"""

import requests
from typing import Optional, Dict, List, Any


class A2AClient:
    """Client for talking to agents"""

    def __init__(self, base_url: str = "http://localhost:8000", agent_name: Optional[str] = None):
        """
        Connect to the agent system

        Args:
            base_url: Agent system URL
            agent_name: Your agent's name
        """
        self.base_url = base_url.rstrip("/")
        self.agent_name = agent_name or "external_agent"
        self.session = requests.Session()

    def discover(self) -> Dict[str, Any]:
        """
        See what agents are available

        Returns info about agents and tools
        """
        response = self.session.get(f"{self.base_url}/api/registry")
        response.raise_for_status()
        return response.json()

    def chat(
        self,
        message: str,
        agent: str = "main",
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Send a message to an agent

        Args:
            message: What you want done
            agent: Which agent (default: "main")
            context: Extra info (optional)

        Returns:
            Response with success status and message

        Example:
            response = client.chat(
                "Create DNS A record for app.example.com",
                agent="network_specialist"
            )
        """
        payload = {
            "message": message,
            "agent": agent,
            "from_agent": self.agent_name,
            "context": context or {}
        }

        response = self.session.post(
            f"{self.base_url}/api/chat",
            json=payload
        )
        response.raise_for_status()
        return response.json()

    def get_status(self) -> Dict[str, Any]:
        """Get system status"""
        response = self.session.get(f"{self.base_url}/api/status")
        response.raise_for_status()
        return response.json()

    def list_agents(self) -> List[str]:
        """Get agent names"""
        registry = self.discover()
        return [agent["name"] for agent in registry["agents"]]

    def delegate_task(
        self,
        task: str,
        agent: str = "main",
        wait_for_completion: bool = True
    ) -> Dict[str, Any]:
        """
        Send a task to an agent (same as chat)

        Args:
            task: What to do
            agent: Which agent
            wait_for_completion: Always waits

        Returns:
            Agent response
        """
        return self.chat(task, agent)


class AgentSwarm:
    """
    Talk to multiple agents at once

    Example:
        swarm = AgentSwarm("http://localhost:8000")
        swarm.broadcast("What's your status?")
    """

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = A2AClient(base_url, agent_name="swarm_coordinator")

    def broadcast(self, message: str) -> List[Dict[str, Any]]:
        """
        Send message to all agents and collect responses

        Args:
            message: Message to broadcast

        Returns:
            List of responses from all agents
        """
        agents = self.client.list_agents()
        responses = []

        for agent in agents:
            try:
                response = self.client.chat(message, agent)
                responses.append({
                    "agent": agent,
                    "response": response
                })
            except Exception as e:
                responses.append({
                    "agent": agent,
                    "error": str(e)
                })

        return responses

    def parallel_delegate(self, tasks: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Delegate multiple tasks to different agents in parallel

        Args:
            tasks: List of {"message": "...", "agent": "..."}

        Returns:
            List of responses

        Example:
            tasks = [
                {"message": "Create subnet 10.0.0.0/24", "agent": "network_specialist"},
                {"message": "List all DNS zones", "agent": "network_specialist"},
                {"message": "Calculate 192.168.1.0/25", "agent": "main"}
            ]
            results = swarm.parallel_delegate(tasks)
        """
        # TODO: Add actual parallel execution with asyncio or threading
        # For now, sequential execution
        results = []
        for task in tasks:
            try:
                response = self.client.chat(
                    task["message"],
                    task.get("agent", "main")
                )
                results.append(response)
            except Exception as e:
                results.append({"error": str(e), "task": task})

        return results


# Convenience function for quick testing
def quick_chat(message: str, agent: str = "main", base_url: str = "http://localhost:8000") -> str:
    """
    Quick one-liner to chat with an agent

    Example:
        from a2a_client import quick_chat
        response = quick_chat("Create subnet 10.0.0.0/24", "network_specialist")
        print(response)
    """
    client = A2AClient(base_url)
    result = client.chat(message, agent)
    return result.get("response", "No response")


if __name__ == "__main__":
    # Demo usage
    print("🤖 A2A Client Demo")
    print("=" * 70)

    # Initialize client
    client = A2AClient("http://localhost:8000", agent_name="demo_agent")

    # Discover agents
    print("\n1️⃣  Discovering agents...")
    registry = client.discover()
    print(f"   Found {len(registry['agents'])} agents:")
    for agent in registry['agents']:
        print(f"   - {agent['name']}: {agent['description']}")

    # Chat with an agent
    print("\n2️⃣  Chatting with network_specialist...")
    response = client.chat(
        message="List all IP spaces in Infoblox",
        agent="network_specialist"
    )
    print(f"   Success: {response['success']}")
    if response['success']:
        print(f"   Response: {response['response'][:200]}...")
        print(f"   Tools used: {len(response['tool_calls'])}")

    print("\n✅ Demo complete!")
