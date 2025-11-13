"""
Example External Agent

This demonstrates how an external agent can communicate with your agent system.
This agent is completely independent and communicates via REST API.

Use Case: Security Compliance Agent
- Monitors network configuration
- Delegates DNS/IPAM tasks to your agents
- Makes autonomous decisions
"""

import asyncio
import time
from a2a_client import A2AClient, AgentSwarm


class SecurityComplianceAgent:
    """
    Example external agent that monitors security compliance

    This agent:
    1. Discovers your agents
    2. Delegates tasks to network_specialist
    3. Makes autonomous decisions
    4. Demonstrates A2A communication
    """

    def __init__(self, name: str = "security_compliance_agent"):
        self.name = name
        self.client = A2AClient("http://localhost:8000", agent_name=name)
        print(f"🤖 {self.name} initialized")

    async def run(self):
        """Main agent loop"""
        print(f"\n{'='*70}")
        print(f"🚀 Starting {self.name}")
        print(f"{'='*70}\n")

        # Step 1: Discover available agents
        print("1️⃣  Discovering available agents...")
        registry = self.client.discover()
        print(f"   ✅ Found {len(registry['agents'])} agents:")
        for agent in registry['agents']:
            print(f"      - {agent['name']}: {agent['description']}")
            print(f"        Capabilities: {', '.join(agent['capabilities'])}")

        # Step 2: Check system status
        print("\n2️⃣  Checking system status...")
        status = self.client.get_status()
        print(f"   ✅ Total tools available: {status.get('total_tools', 0)}")
        print(f"   ✅ MCP servers: {len(status.get('mcp_servers', []))}")

        # Step 3: Audit DNS records
        print("\n3️⃣  Auditing DNS records (delegating to network_specialist)...")
        try:
            response = self.client.chat(
                message="List all DNS A records in the system",
                agent="network_specialist"
            )

            if response['success']:
                print(f"   ✅ Got response from network_specialist")
                print(f"   📊 Tools used: {len(response.get('tool_calls', []))}")
                print(f"   💬 Response preview: {response['response'][:150]}...")
            else:
                print(f"   ❌ Error: {response.get('error')}")
        except Exception as e:
            print(f"   ❌ Failed to communicate: {e}")

        # Step 4: Check IP space allocation
        print("\n4️⃣  Checking IP space allocation...")
        try:
            response = self.client.chat(
                message="List all IP spaces and subnets",
                agent="network_specialist"
            )

            if response['success']:
                print(f"   ✅ IP space audit complete")
                print(f"   💬 {response['response'][:150]}...")
        except Exception as e:
            print(f"   ❌ Failed: {e}")

        # Step 5: Make autonomous decision
        print("\n5️⃣  Making autonomous decision based on findings...")
        print("   🤔 Analyzing network configuration...")
        time.sleep(1)  # Simulate thinking
        print("   ✅ Network configuration looks good!")

        print(f"\n{'='*70}")
        print(f"✅ {self.name} completed successfully!")
        print(f"{'='*70}\n")


class AutomatedNetworkProvisioner:
    """
    Example: Automated network provisioning agent

    Demonstrates multi-step workflow delegation
    """

    def __init__(self):
        self.name = "network_provisioner"
        self.client = A2AClient("http://localhost:8000", agent_name=self.name)

    async def provision_application(self, app_name: str, subnet: str):
        """
        Provision network resources for a new application

        This demonstrates a multi-step workflow:
        1. Create subnet
        2. Create DNS zone
        3. Create DNS A record
        """
        print(f"\n🚀 Provisioning network for application: {app_name}")
        print("=" * 70)

        tasks = []

        # Task 1: Create subnet
        print("\n1️⃣  Creating subnet...")
        response1 = self.client.chat(
            f"Create subnet {subnet} with comment 'Application: {app_name}'",
            agent="network_specialist"
        )
        if response1['success']:
            print(f"   ✅ Subnet created: {subnet}")
            tasks.append({"step": "subnet", "success": True})
        else:
            print(f"   ❌ Failed: {response1.get('error')}")
            tasks.append({"step": "subnet", "success": False})

        # Task 2: Create DNS A record
        print("\n2️⃣  Creating DNS A record...")
        ip = subnet.split('/')[0]  # Simple: use first IP
        response2 = self.client.chat(
            f"Create DNS A record for {app_name}.infolab.com pointing to {ip}",
            agent="network_specialist"
        )
        if response2['success']:
            print(f"   ✅ DNS record created: {app_name}.infolab.com -> {ip}")
            tasks.append({"step": "dns", "success": True})
        else:
            print(f"   ❌ Failed: {response2.get('error')}")
            tasks.append({"step": "dns", "success": False})

        # Summary
        print("\n" + "=" * 70)
        successes = sum(1 for t in tasks if t['success'])
        print(f"✅ Provisioning complete: {successes}/{len(tasks)} tasks succeeded")
        print("=" * 70 + "\n")

        return tasks


class SwarmCoordinator:
    """
    Example: Swarm coordinator that manages multiple agents

    Demonstrates broadcast and parallel delegation
    """

    def __init__(self):
        self.swarm = AgentSwarm("http://localhost:8000")

    async def coordinate(self):
        """Coordinate multiple agents"""
        print("\n🐝 Swarm Coordinator starting...")
        print("=" * 70)

        # Broadcast to all agents
        print("\n1️⃣  Broadcasting health check to all agents...")
        responses = self.swarm.broadcast("What is your current status?")

        for resp in responses:
            agent = resp.get('agent', 'unknown')
            if 'error' in resp:
                print(f"   ❌ {agent}: {resp['error']}")
            else:
                response_data = resp.get('response', {})
                print(f"   ✅ {agent}: Online")

        # Parallel task delegation
        print("\n2️⃣  Delegating tasks in parallel...")
        tasks = [
            {"message": "List all IP spaces", "agent": "network_specialist"},
            {"message": "List all DNS zones", "agent": "network_specialist"},
        ]

        results = self.swarm.parallel_delegate(tasks)
        print(f"   ✅ Completed {len(results)} tasks")

        print("\n" + "=" * 70)
        print("✅ Swarm coordination complete!")
        print("=" * 70 + "\n")


async def main():
    """
    Main demo - run different external agent examples
    """
    print("\n" + "=" * 70)
    print("🤖 External Agent Demo - Agent-to-Agent Communication")
    print("=" * 70)

    choice = input("""
Choose a demo:
1. Security Compliance Agent (monitors and audits)
2. Network Provisioner (multi-step workflow)
3. Swarm Coordinator (broadcast to multiple agents)
4. Simple Test (quick chat)

Enter choice (1-4): """)

    if choice == "1":
        agent = SecurityComplianceAgent()
        await agent.run()

    elif choice == "2":
        agent = AutomatedNetworkProvisioner()
        await agent.provision_application("myapp", "10.20.30.0/24")

    elif choice == "3":
        coordinator = SwarmCoordinator()
        await coordinator.coordinate()

    elif choice == "4":
        print("\n🧪 Simple Test")
        print("=" * 70)
        client = A2AClient("http://localhost:8000", agent_name="test_agent")

        print("\nSending: 'List all DNS zones'")
        response = client.chat("List all DNS zones", "network_specialist")

        print(f"\nSuccess: {response.get('success')}")
        print(f"Response: {response.get('response', 'No response')[:300]}")
        print("=" * 70 + "\n")

    else:
        print("Invalid choice")


if __name__ == "__main__":
    asyncio.run(main())
