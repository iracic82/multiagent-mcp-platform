# 🚀 Quick Start Guide

Get your multi-agent system with Infoblox integration running in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Configure API Keys

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your API key(s)
nano .env  # or use your favorite editor
```

Add at minimum:
```bash
ANTHROPIC_API_KEY=sk-ant-...your-key-here
```

Optionally add:
```bash
OPENAI_API_KEY=sk-...your-key-here
INFOBLOX_API_KEY=your-infoblox-key-here
INFOBLOX_BASE_URL=https://csp.infoblox.com
```

## Step 3: Start MCP Servers

**Option 1: Start All HTTP Servers (Recommended - Spec-Compliant)**

```bash
./start_http_servers.sh
```

This launches all 4 HTTP MCP servers in parallel. Expected output:
```
Starting HTTP MCP Servers...
✅ Infoblox DDI HTTP Server (port 4001)
✅ Subnet Calculator HTTP Server (port 4002)
✅ AWS Tools HTTP Server (port 4003)
✅ AWS CloudControl HTTP Server (port 4004)

All servers started. Press Ctrl+C to stop all servers.
```

**Option 2: Start Servers Individually**

Open 4 terminal windows:

**Terminal 1 - Infoblox MCP Server:**
```bash
source venv/bin/activate
python mcp_infoblox_http.py  # Port 4001/mcp (HTTP)
# or: python mcp_infoblox.py  # Port 3001/sse (SSE backup)
```

**Terminal 2 - Subnet Calculator MCP Server:**
```bash
source venv/bin/activate
python mcp_server_http.py     # Port 4002/mcp (HTTP)
# or: python mcp_server.py     # Port 3002/sse (SSE backup)
```

**Terminal 3 - AWS Tools MCP Server:**
```bash
source venv/bin/activate
python mcp_aws_http.py         # Port 4003/mcp (HTTP)
# or: python mcp_aws.py         # Port 3003/sse (SSE backup)
```

**Terminal 4 - AWS CloudControl MCP Server:**
```bash
source venv/bin/activate
python mcp_aws_cloudcontrol_http.py  # Port 4004/mcp (HTTP)
# or: python mcp_aws_cloudcontrol.py  # Port 3004/sse (SSE backup)
```

Expected output for HTTP servers:
```
Infoblox BloxOne DDI: HTTP server running on http://127.0.0.1:4001/mcp
Subnet Calculator: HTTP server running on http://127.0.0.1:4002/mcp
AWS Tools: HTTP server running on http://127.0.0.1:4003/mcp
AWS CloudControl: HTTP server running on http://127.0.0.1:4004/mcp
```

## Step 4: Start Web Server

**New Terminal - Web Server:**
```bash
source venv/bin/activate
python web_server.py
```

Expected output:
```
🚀 Starting Multi-Agent System...
✅ Connected to infoblox-ddi via HTTP (spec-compliant) - 98 tools
✅ Connected to subnet-calculator via HTTP (spec-compliant) - 2 tools
✅ Connected to aws-tools via HTTP (spec-compliant) - 27 tools
✅ Connected to aws-cloudcontrol via HTTP (spec-compliant) - 6 tools
✓ Created agent: main (claude)
✓ Created agent: network_specialist (claude)
✅ System initialized successfully!
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Note: The system connects to HTTP servers (ports 4001-4004) by default. If HTTP servers are not available, it falls back to SSE servers (ports 3001-3004).

## Step 5: Open Browser

Navigate to: **http://localhost:8000**

The interface displays:
- Purple gradient sidebar with system status
- Chat interface in the center
- Agent selector dropdown
- MCP server count: 4
- Total tools: 133

## Step 6: Start Chatting!

Try these examples:

### Subnet Calculations
```
Calculate subnet information for 192.168.1.0/24
```

Expected response: Network details with markdown formatting

### Infoblox Operations (if API key configured)
```
List my IP spaces
```

```
Show me subnet utilization
```

Expected: Table with **automatic pie and bar charts**! 📊📈

### Complex Workflows
```
I need to design a network with:
- 3 subnets for different departments
- Each subnet needs 50 hosts
- Starting from 10.0.0.0/16

Please calculate the optimal subnets.
```

### DNS Management (if Infoblox configured)
```
Create an A record for web pointing to 192.168.1.100
```

```
List all my DNS zones
```

## What You Get

### Real-Time Features
- ✅ **WebSocket chat** - Instant responses
- ✅ **Typing indicators** - See when agent is thinking
- ✅ **Connection status** - Monitor system health

### Visual Features
- ✅ **Auto-generated charts** - Pie and bar charts from tables
- ✅ **Markdown rendering** - Beautiful formatted responses
- ✅ **Code highlighting** - Syntax highlighting for technical data
- ✅ **Tool visualization** - See which tools are called

### Agent Features
- ✅ **Agent switching** - Toggle between main and network_specialist
- ✅ **Multi-agent delegation** - Agents collaborate automatically
- ✅ **Tool access** - 133 tools from 4 MCP servers

## System Status Dashboard

The sidebar displays:
- **MCP Servers**: Shows "4" (Infoblox DDI, Subnet Calc, AWS Tools, AWS CloudControl)
- **Agents**: Shows "2" (main, network_specialist)
- **Tools**: Shows "133" (98 Infoblox + 2 Subnet + 27 AWS + 6 CloudControl)
- **Status**: Green dot indicates "Online"

## Chart Generation

When you ask for subnet utilization, the system automatically:
1. Calls Infoblox API
2. Formats response as markdown table
3. **Auto-detects** table has utilization data
4. **Auto-generates** two charts:
   - 📊 Doughnut chart showing proportional usage
   - 📈 Bar chart showing used vs free capacity

No manual action needed - it's automatic!

## Troubleshooting

### "Connection error. Please refresh the page."
- Check that `web_server.py` is running on port 8000
- Refresh the browser
- Check browser console for errors

### "0 MCP Servers, 0 Tools"
- Ensure all HTTP MCP servers are running (run `./start_http_servers.sh`)
- Check servers are on ports 4001-4004 (HTTP) or 3001-3004 (SSE backup)
- Restart web_server.py to reconnect

### "API key not found"
- Check `.env` file exists
- Verify `ANTHROPIC_API_KEY` is set
- Restart web_server.py after updating `.env`

### "Infoblox client not initialized"
- Check `INFOBLOX_API_KEY` in `.env`
- Verify API key is valid
- Restart `mcp_infoblox_http.py` (or `mcp_infoblox.py` for SSE)

### Charts not showing
- Ensure query returns table format
- Check table has "Utilization %" or "%" column
- Open browser console to see JavaScript errors

## Next Steps

### Add More MCP Servers

1. Edit `mcp_config.json`
2. Set `"enabled": true` on any server
3. Restart web_server.py

Example MCP servers ready to enable:
- AWS operations
- Terraform infrastructure
- GitHub integration
- File operations
- Web search
- Database operations

### Create Specialized Agents

1. Edit `mcp_config.json`
2. Add your agent config:
```json
{
  "name": "security_expert",
  "llm_provider": "claude",
  "system_prompt": "You are a cybersecurity specialist...",
  "enabled": true
}
```
3. Restart web_server.py
4. Agent appears in dropdown!

### Use Programmatically

```python
import asyncio
from agents.orchestrator import get_orchestrator

async def main():
    orch = get_orchestrator()

    await orch.initialize(
        mcp_servers=[
            {"name": "infoblox-ddi", "url": "http://127.0.0.1:4001/mcp"},
            {"name": "subnet-calculator", "url": "http://127.0.0.1:4002/mcp"},
            {"name": "aws-tools", "url": "http://127.0.0.1:4003/mcp"},
            {"name": "aws-cloudcontrol", "url": "http://127.0.0.1:4004/mcp"}
        ],
        agent_configs=[
            {"name": "main", "llm_provider": "claude"}
        ]
    )

    response = await orch.chat("Calculate 10.0.0.0/8", "main")
    print(response["response"])

    await orch.cleanup()

asyncio.run(main())
```

## Quick Commands Reference

```bash
# Start everything (recommended)
./start_http_servers.sh     # Starts all 4 HTTP MCP servers
python web_server.py        # In a new terminal

# Or start individually
python mcp_infoblox_http.py           # Terminal 1 (HTTP)
python mcp_server_http.py             # Terminal 2 (HTTP)
python mcp_aws_http.py                # Terminal 3 (HTTP)
python mcp_aws_cloudcontrol_http.py   # Terminal 4 (HTTP)
python web_server.py                  # Terminal 5

# Then open: http://localhost:8000

# Stop everything
# Press Ctrl+C in each terminal
```

## Getting Help

- Check **README.md** for full documentation
- Check **TECHNOLOGY_STACK.md** for all tools used
- Check **CLAUDE.md** for development guide
- Check **ARCHITECTURE.md** for system design
- Check **INFOBLOX_SETUP.md** for Infoblox details
- Run tests: `python test_agent.py`

## What's Next?

Explore the codebase:
- **agents/** - Multi-agent framework
- **services/** - Business logic
- **static/** - Web UI with charts
- **mcp_config.json** - Add servers/agents
- **web_server.py** - WebSocket + FastAPI
- **mcp_*.py** - MCP server implementations

## Pro Tips

1. **Use parallel launcher** - `./start_http_servers.sh` starts all 4 servers at once
2. **Check system status** - Sidebar shows connection health
3. **Try complex queries** - Agent handles multi-step workflows
4. **Ask for tables** - Triggers automatic chart generation
5. **Switch agents** - network_specialist for Infoblox/networking tasks
6. **Tool calls visible** - Expand to see API details
7. **HTTP is primary** - Spec-compliant transport with SSE backup available

Happy building! 🎉

---

**Estimated time to first query: 5 minutes**
**Features unlocked: Real-time chat, auto-charts, markdown, 133 tools, 4 MCP servers, 2 agents, VPN automation, DNS security, AWS management**
