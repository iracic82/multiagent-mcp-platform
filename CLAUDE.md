# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **production-ready multi-agent system** with MCP (Model Context Protocol) integration. It combines multiple LLMs (Claude and OpenAI) with multiple MCP servers to create a flexible, extensible agent platform with a Streamlit UI.

**Core Capabilities:**
- Multi-LLM support (Claude + OpenAI)
- Multi-MCP server integration (subnet calculator, AWS, Terraform, etc.)
- Agent-to-agent delegation
- Production web UI with Streamlit

## Architecture

### Agent Layer (agents/)

**base_agent.py**: Core agent implementation
- Supports both Claude and OpenAI as LLM providers
- Calls MCP tools from any connected server
- Can delegate tasks to other agents
- Maintains conversation history and context

**mcp_client.py**: MCP server client
- Connects to multiple MCP servers simultaneously
- Manages tool discovery and execution
- Handles server lifecycle (connect/disconnect)
- Thread-safe singleton pattern

**orchestrator.py**: Multi-agent orchestration
- Manages all agents and MCP connections
- Handles initialization and cleanup
- Routes messages between agents
- Provides system status and monitoring

### MCP Server Layer

**mcp_server.py**: Subnet calculator MCP server
- FastMCP-based implementation
- Tools: `calculate_subnet_info`, `validate_cidr`
- Stdio transport (JSON-RPC)

**mcp_config.json**: MCP server configurations
- Defines all available MCP servers
- Agent configurations
- Easy to add AWS, Terraform, GitHub, etc.

### Service Layer (services/)

**subnet_calc.py**: Core subnet calculation logic
- Uses Python's ipaddress module
- Handles CIDR notation with strict=False

### UI Layer

**app.py**: Streamlit production UI
- Chat interface with agents
- Real-time tool call visualization
- MCP server management
- Agent switching and configuration

### Legacy REST API (optional)

**main.py, routers/, models/, client/**: FastAPI REST API
- Can run alongside agent system if needed

## Running the System

### 1. Setup

Install dependencies:
```bash
pip install -r requirements.txt
```

Configure API keys:
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY (required)
# Optionally add OPENAI_API_KEY for GPT models
```

### 2. Run the Agent System (Recommended)

Launch Streamlit UI:
```bash
streamlit run app.py
```

Opens at http://localhost:8501 with:
- Chat interface
- Agent selection
- MCP server management
- Real-time tool visualization

### 3. Test the System

Run test suite:
```bash
python test_agent.py
```

### 4. Run Standalone MCP Server

For debugging or Claude Desktop integration:
```bash
fastmcp dev mcp_server.py
```

Install in Claude Desktop:
```bash
fastmcp install mcp_server.py
```

## Common Development Tasks

### Adding a New MCP Server

1. Edit `mcp_config.json`:
```json
{
  "mcpServers": {
    "your-server": {
      "command": "python",
      "args": ["your_server.py"],
      "enabled": true
    }
  }
}
```

2. Restart the system - agents will auto-discover tools

### Creating a Specialized Agent

1. Add to `mcp_config.json`:
```json
{
  "agentConfigs": [
    {
      "name": "specialist",
      "llm_provider": "claude",
      "system_prompt": "You specialize in...",
      "enabled": true
    }
  ]
}
```

2. Access via UI dropdown or programmatically

### Testing MCP Tools

Test core logic:
```bash
python test_mcp.py
```

Test with MCP Inspector UI:
```bash
fastmcp dev mcp_server.py
# Opens http://localhost:5173
```

### Programmatic Usage

```python
import asyncio
from agents.orchestrator import get_orchestrator

async def main():
    orchestrator = get_orchestrator()

    # Initialize with MCP servers
    await orchestrator.initialize(
        mcp_servers=[
            {"name": "subnet", "command": "python", "args": ["mcp_server.py"]}
        ],
        agent_configs=[
            {"name": "main", "llm_provider": "claude"}
        ]
    )

    # Chat with agent
    response = await orchestrator.chat("Calculate 192.168.1.0/24", "main")
    print(response["response"])

    # Cleanup
    await orchestrator.cleanup()

asyncio.run(main())
```

## Key Files for Modification

- **agents/base_agent.py**: Core agent logic, add capabilities here
- **agents/orchestrator.py**: Multi-agent coordination
- **mcp_config.json**: All MCP and agent configurations
- **app.py**: UI customization
- **mcp_server.py**: Subnet calculator tools

## Dependencies

Core:
- `fastmcp>=2.0.0` - MCP server framework
- `anthropic>=0.40.0` - Claude API
- `openai>=1.0.0` - OpenAI API
- `mcp>=1.2.0` - MCP client SDK
- `streamlit>=1.30.0` - Production UI
- `python-dotenv` - Environment management

## Troubleshooting

**Import errors**: Run `pip install -r requirements.txt`

**API key errors**: Check `.env` file has valid keys

**MCP connection fails**:
- Verify server command in `mcp_config.json`
- Check server is executable
- Review logs in terminal

**Agent not responding**:
- Check API quota/billing
- Verify correct model names in `.env`
- Check network connectivity
