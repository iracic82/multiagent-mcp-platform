"""
Example: External System Connecting to YOUR Agent API

This shows how another developer's system can connect to your agent
via REST API and get intelligent responses (not just raw tool calls).
"""

import requests
import json


class ExternalSystemClient:
    """
    An external system (from another developer/company) that wants to use
    YOUR intelligent agent, not just the MCP tools.

    This is useful when you want:
    1. The agent's reasoning and intelligence
    2. Multiple tools orchestrated together
    3. Natural language interface
    """

    def __init__(self, agent_api_url: str, api_key: str = None):
        """
        Args:
            agent_api_url: Base URL of your agent API (e.g., "http://your-domain.com:8000")
            api_key: Optional API key for authentication
        """
        self.base_url = agent_api_url
        self.api_key = api_key
        self.session = requests.Session()

        if api_key:
            self.session.headers.update({
                "Authorization": f"Bearer {api_key}"
            })

    def get_status(self):
        """Check if the agent system is available"""
        response = self.session.get(f"{self.base_url}/api/status")
        return response.json()

    def chat(self, message: str, agent_name: str = "main"):
        """
        Send a message to the agent and get an intelligent response.

        The agent will:
        - Understand your natural language request
        - Choose appropriate tools
        - Call multiple MCP servers if needed
        - Return a formatted, human-readable response
        """
        response = self.session.post(
            f"{self.base_url}/api/chat",
            json={
                "message": message,
                "agent_name": agent_name
            }
        )
        return response.json()

    def print_response(self, response: dict):
        """Pretty print agent response"""
        print(f"\n{'='*60}")
        print(f"Agent: {response.get('agent')}")
        print(f"LLM: {response.get('llm_provider')}")
        print(f"{'='*60}")
        print(f"\n{response.get('response')}")

        if response.get('tool_calls'):
            print(f"\n🔧 Tool Calls Made:")
            for tool_call in response['tool_calls']:
                print(f"   - {tool_call['tool']}")
                print(f"     Input: {json.dumps(tool_call['input'], indent=6)}")

        if response.get('error'):
            print(f"\n❌ Error: {response['error']}")
        print(f"\n{'='*60}")


def main():
    """
    Demo: External system using YOUR agent API
    """
    print("="*60)
    print("EXTERNAL SYSTEM CONNECTING TO YOUR AGENT API")
    print("="*60)

    # Connect to your agent API
    client = ExternalSystemClient(
        agent_api_url="http://localhost:8000",
        api_key="your-api-key-here"  # You would add auth to api_server.py
    )

    # Check system status
    print("\n📊 Checking system status...")
    status = client.get_status()
    print(f"Initialized: {status['initialized']}")
    print(f"Agents: {list(status['agents'].keys())}")
    print(f"MCP Servers: {list(status['mcp_servers'].keys())}")
    print(f"Total Tools: {status['total_tools']}")

    # Example 1: Simple subnet calculation
    print("\n\n🔹 Example 1: Simple subnet calculation")
    response = client.chat("What's the subnet info for 192.168.1.0/24?")
    client.print_response(response)

    # Example 2: Complex multi-step request
    print("\n\n🔹 Example 2: Complex request")
    response = client.chat(
        "I need to set up 3 subnets in the 10.0.0.0/16 range, "
        "one for web servers, one for app servers, and one for databases. "
        "Calculate the subnet ranges for me."
    )
    client.print_response(response)

    # Example 3: Validation
    print("\n\n🔹 Example 3: Validation")
    response = client.chat("Is 256.300.1.0/24 a valid CIDR?")
    client.print_response(response)


if __name__ == "__main__":
    main()
