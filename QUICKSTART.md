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

Open 2 terminal windows:

**Terminal 1 - Infoblox MCP Server:**
```bash
source venv/bin/activate
python mcp_infoblox.py
```

**Terminal 2 - Subnet Calculator MCP Server:**
```bash
source venv/bin/activate
python mcp_server.py
```

You should see:
```
Infoblox BloxOne DDI: SSE server running on http://127.0.0.1:3001/sse
Subnet Calculator: SSE server running on http://127.0.0.1:3002/sse
```

## Step 4: Start Web Server

**Terminal 3 - Web Server:**
```bash
source venv/bin/activate
python web_server.py
```

You should see:
```
🚀 Starting Multi-Agent System...
✓ Connected to MCP server: subnet-calculator (http://127.0.0.1:3002/sse)
  Available tools: 2
✓ Connected to MCP server: infoblox-ddi (http://127.0.0.1:3001/sse)
  Available tools: 48
✓ Created agent: main (claude)
✓ Created agent: network_specialist (claude)
✅ System initialized successfully!
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Step 5: Open Browser

Navigate to: **http://localhost:8000**

You should see:
- Purple gradient sidebar with system status
- Chat interface in the center
- Agent selector dropdown
- MCP server count: 2
- Total tools: 50

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
- ✅ **Tool access** - 50 tools from 2 MCP servers (+ Terraform MCP)

## System Status Dashboard

The sidebar shows:
- **MCP Servers**: Should show "2"
- **Agents**: Should show "2"
- **Tools**: Should show "50"
- **Status**: Should show green dot and "Online"

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
- Ensure both MCP servers are running
- Check they're on ports 3001 and 3002
- Restart web_server.py to reconnect

### "API key not found"
- Check `.env` file exists
- Verify `ANTHROPIC_API_KEY` is set
- Restart web_server.py after updating `.env`

### "Infoblox client not initialized"
- Check `INFOBLOX_API_KEY` in `.env`
- Verify API key is valid
- Restart `mcp_infoblox.py`

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
            {"name": "subnet-calculator", "url": "http://127.0.0.1:3002/sse"},
            {"name": "infoblox-ddi", "url": "http://127.0.0.1:3001/sse"}
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
# Start everything
python mcp_infoblox.py     # Terminal 1
python mcp_server.py        # Terminal 2
python web_server.py        # Terminal 3

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

1. **Keep terminals open** - You need all 3 running
2. **Check system status** - Sidebar shows connection health
3. **Try complex queries** - Agent handles multi-step workflows
4. **Ask for tables** - Triggers automatic chart generation
5. **Switch agents** - network_specialist for Infoblox tasks
6. **Tool calls visible** - Expand to see API details

Happy building! 🎉

---

**Estimated time to first query: 5 minutes**
**Features unlocked: Real-time chat, auto-charts, markdown, 50 tools, 2 agents, VPN automation, DNS security**
