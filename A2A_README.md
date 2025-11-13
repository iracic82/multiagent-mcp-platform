# Agent-to-Agent (A2A) Communication Guide

## Overview

Your agent system now supports **Agent-to-Agent (A2A) communication** via REST API. External agents can discover, communicate with, and delegate tasks to your agents without needing MCP SDK or special protocols.

## Quick Start

### 1. Discover Available Agents

```bash
curl http://localhost:8000/api/registry
```

**Response:**
```json
{
  "agents": [
    {
      "name": "main",
      "llm_provider": "claude",
      "endpoint": "http://localhost:8000/api/chat",
      "description": "General purpose agent",
      "capabilities": ["subnet-calculator: 2 tools", "infoblox-ddi: 103 tools"]
    },
    {
      "name": "network_specialist",
      "llm_provider": "claude",
      "endpoint": "http://localhost:8000/api/chat",
      "description": "Network and infrastructure specialist",
      "capabilities": ["subnet-calculator: 2 tools", "infoblox-ddi: 103 tools"]
    }
  ],
  "total_tools": 105,
  "version": "1.0.0",
  "protocol": "A2A-REST"
}
```

### 2. Chat with an Agent

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create subnet 10.0.0.0/24",
    "agent": "network_specialist",
    "from_agent": "my_external_agent"
  }'
```

**Response:**
```json
{
  "success": true,
  "response": "I created the subnet successfully...",
  "tool_calls": [{...}],
  "agent": "network_specialist",
  "to_agent": "my_external_agent"
}
```

## Python Client Library

### Installation

```python
# Copy a2a_client.py to your project
from a2a_client import A2AClient
```

### Basic Usage

```python
from a2a_client import A2AClient

# Connect to agent system
client = A2AClient("http://localhost:8000", agent_name="my_agent")

# Discover agents
registry = client.discover()
print(f"Found {len(registry['agents'])} agents")

# Chat with network specialist
response = client.chat(
    message="List all DNS zones",
    agent="network_specialist"
)

print(response['response'])
```

### Advanced Usage - Swarm Behavior

```python
from a2a_client import AgentSwarm

swarm = AgentSwarm("http://localhost:8000")

# Broadcast to all agents
responses = swarm.broadcast("What is your status?")

# Parallel task delegation
tasks = [
    {"message": "List IP spaces", "agent": "network_specialist"},
    {"message": "Calculate 192.168.1.0/24", "agent": "main"}
]
results = swarm.parallel_delegate(tasks)
```

## External Agent Examples

### Example 1: Security Compliance Agent

```python
from a2a_client import A2AClient
import asyncio

class SecurityAgent:
    def __init__(self):
        self.client = A2AClient("http://localhost:8000",
                                agent_name="security_scanner")

    async def audit_network(self):
        # Delegate DNS audit to network_specialist
        response = self.client.chat(
            "List all DNS A records",
            agent="network_specialist"
        )

        # Analyze results
        if response['success']:
            dns_records = response['response']
            print(f"Found records: {dns_records}")
            # Perform security analysis...
```

### Example 2: Automated Provisioner

```python
class NetworkProvisioner:
    def __init__(self):
        self.client = A2AClient("http://localhost:8000",
                                agent_name="provisioner")

    def provision_app(self, app_name, subnet):
        # Step 1: Create subnet
        response1 = self.client.chat(
            f"Create subnet {subnet} for {app_name}",
            agent="network_specialist"
        )

        # Step 2: Create DNS record
        response2 = self.client.chat(
            f"Create DNS A record for {app_name}.example.com",
            agent="network_specialist"
        )

        return {
            "subnet": response1['success'],
            "dns": response2['success']
        }
```

## API Endpoints

### GET `/api/registry`
Discover available agents and their capabilities.

**Response:**
- `agents[]`: List of available agents
- `total_tools`: Total MCP tools available
- `mcp_servers{}`: Connected MCP servers
- `version`: API version
- `protocol`: Communication protocol (A2A-REST)

### POST `/api/chat`
Send a message to an agent.

**Request Body:**
```json
{
  "message": "Your message here",
  "agent": "main" (optional, defaults to "main"),
  "from_agent": "your_agent_name" (optional),
  "context": {} (optional, additional context)
}
```

**Response:**
```json
{
  "success": true/false,
  "response": "Agent's response text",
  "tool_calls": [list of tools used],
  "agent": "agent_name",
  "to_agent": "from_agent_name"
}
```

### GET `/api/status`
Get system status (existing endpoint).

### GET `/api/agents`
Get list of available agents (existing endpoint).

## Architecture

```
External Agent (any language/framework)
    ↓ HTTP POST /api/chat
FastAPI Web Server (web_server.py)
    ↓ orchestrator.chat()
Agent Orchestrator
    ↓
Your Agent (main / network_specialist)
    ↓ MCP tools
Infoblox MCP Server (103 tools)
Subnet Calculator MCP Server (2 tools)
    ↓
Infoblox API / Subnet calculations
```

## Use Cases

### 1. Multi-Agent Orchestration
Build a coordinator agent that delegates subtasks to specialized agents.

### 2. Agent Swarms
Create multiple autonomous agents that communicate and collaborate.

### 3. Workflow Automation
Chain multiple agents for complex multi-step workflows.

### 4. Microservices Integration
Integrate your agents into existing microservice architectures.

### 5. External Tool Integration
Allow external systems (CI/CD, monitoring, etc.) to leverage your agents.

## Testing

### Test Agent Discovery
```bash
curl http://localhost:8000/api/registry | jq .
```

### Test Chat Endpoint
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "List all DNS zones", "agent": "network_specialist"}'
```

### Run Example External Agent
```bash
python3 example_external_agent.py
```

Choose option 4 for a simple test.

## Benefits of A2A vs MCP

✅ **Simpler** - Just HTTP, no MCP SDK required
✅ **Language Agnostic** - Works with Python, Node, Go, Java, etc.
✅ **Flexible** - Design your own agent protocols
✅ **Scalable** - Easy to scale to 100s of agents
✅ **Standard** - Uses REST API everyone understands

## Next Steps

1. **Run the demo**: `python3 example_external_agent.py`
2. **Build your agent**: Use `a2a_client.py` as starting point
3. **Create swarms**: Use `AgentSwarm` for multi-agent coordination
4. **Scale up**: Deploy multiple external agents

## Files

- `a2a_client.py` - Python client library
- `example_external_agent.py` - Complete working examples
- `web_server.py` - REST API endpoints (lines 119-244)
- `A2A_README.md` - This file

## Troubleshooting

**Port already in use:**
```bash
lsof -ti:8000 | xargs kill -9
python3 web_server.py
```

**Connection refused:**
- Check servers are running: `curl http://localhost:8000/api/status`
- Verify ports 3001, 3002, 8000 are open

**Agent not found:**
- List available agents: `curl http://localhost:8000/api/agents`
- Use exact agent name: "main" or "network_specialist"

## Security Considerations

🔐 **Production Deployment:**
- Add API authentication (JWT, API keys)
- Use HTTPS/TLS
- Implement rate limiting
- Add agent authorization
- Log all A2A communications

This system currently has no authentication - suitable for local development only.

## Support

For issues or questions:
1. Check the logs: Watch terminal output from `web_server.py`
2. Test with curl first before using client library
3. Review `example_external_agent.py` for working code patterns

---

**🎉 You now have a complete Agent-to-Agent communication system!**

External agents can discover, communicate with, and delegate to your agents using simple REST APIs - no MCP required!
