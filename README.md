# Multi-Agent MCP System with Infoblox Integration

A production-ready multi-agent system that combines Claude and OpenAI LLMs with Model Context Protocol (MCP) servers for network management, IPAM, DNS, VPN provisioning, and infrastructure automation.

## 🚀 Features

- **Multi-LLM Support**: Use both Claude (Anthropic) and OpenAI GPT models
- **Multi-MCP Integration**: Connect to multiple MCP servers simultaneously (3 active servers, 59 tools)
- **Infoblox BloxOne DDI**: Complete IPAM, DNS Data, DNS Config, and Federation API integration
- **NIOSXaaS VPN**: Full VPN Universal Service provisioning with consolidated API
- **Atcfw/DFP Security**: DNS Firewall Protection with threat intelligence and content filtering
- **Terraform MCP**: Infrastructure as Code with AWS best practices
- **Agent Orchestration**: Multiple specialized agents that can delegate to each other
- **Modern Web UI**: FastAPI backend with WebSocket real-time chat + Chart.js visualizations
- **Auto-Visualization**: Automatic chart generation from subnet utilization data
- **End-to-End VPN Automation**: Complete workflow from Infoblox NIOSXaaS to AWS VPC VPN setup
- **Extensible**: Easy to add new MCP servers and agents

## 📋 Prerequisites

- Python 3.10+
- API Keys:
  - Anthropic API key (for Claude) - **required**
  - OpenAI API key (for GPT models) - optional
  - Infoblox API key (for DDI operations) - optional

## 🛠️ Installation

1. **Clone and navigate to the project:**
   ```bash
   cd subnet_mcp
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

4. **Edit `.env` file:**
   ```bash
   ANTHROPIC_API_KEY=your_anthropic_key_here
   OPENAI_API_KEY=your_openai_key_here  # optional
   INFOBLOX_API_KEY=your_infoblox_key_here  # optional
   INFOBLOX_BASE_URL=https://csp.infoblox.com
   ```

## 🎯 Quick Start

### Next.js Frontend (Recommended)

**Step 1: Start Backend Services**

```bash
# Terminal 1: Start Infoblox MCP server
source venv/bin/activate
python mcp_infoblox.py

# Terminal 2: Start Subnet Calculator MCP server
source venv/bin/activate
python mcp_server.py

# Terminal 3: Start FastAPI backend server
source venv/bin/activate
python main.py  # Or your backend entry point
```

**Step 2: Start Frontend**

```bash
# Terminal 4: Start Next.js frontend
cd frontend-v2
npm install  # First time only
npm run dev
```

**Step 3: Open Browser**

Navigate to `http://localhost:3006`

The UI includes:
- Next.js 14 + TypeScript + shadcn/ui
- Real-time WebSocket chat
- Agent selection
- Dark mode toggle
- System status dashboard (MCP servers, agents, tools count)
- Markdown rendering with GitHub Flavored Markdown
- Accessible UI with Radix primitives
- Professional component library

See [FRONTEND.md](FRONTEND.md) for complete frontend documentation.

### Alternative: Command Line Testing

Test the agent system programmatically:

```bash
python test_agent.py
```

## 🔧 Configuration

### MCP Server Management

Edit `mcp_config.json` to configure MCP servers and agents:

```json
{
  "mcpServers": {
    "subnet-calculator": {
      "description": "Local subnet calculator",
      "command": "python",
      "args": ["mcp_server.py"],
      "enabled": true
    },
    "infoblox-ddi": {
      "description": "Infoblox BloxOne DDI - IPAM, DNS Data, and DNS Config",
      "command": "python",
      "args": ["mcp_infoblox.py"],
      "env": {
        "INFOBLOX_API_KEY": "${INFOBLOX_API_KEY}",
        "INFOBLOX_BASE_URL": "${INFOBLOX_BASE_URL}"
      },
      "enabled": true
    }
  },
  "agentConfigs": [
    {
      "name": "main",
      "llm_provider": "claude",
      "system_prompt": "...",
      "enabled": true
    },
    {
      "name": "network_specialist",
      "llm_provider": "claude",
      "system_prompt": "Network specialist with Infoblox expertise...",
      "enabled": true
    }
  ]
}
```

**Available MCP Servers** (examples in config):
- ✅ **subnet-calculator**: Local subnet calculations (included)
- ✅ **infoblox-ddi**: Infoblox IPAM, DNS, DHCP management (included)
- 🔌 **aws-mcp**: AWS resource management
- 🔌 **terraform-mcp**: Infrastructure as code
- 🔌 **filesystem-mcp**: File operations
- 🔌 **github-mcp**: GitHub API integration
- 🔌 **brave-search-mcp**: Web search
- 🔌 **postgres-mcp**: Database operations

## 📁 Project Structure

```
subnet_mcp/
├── agents/                     # Agent framework
│   ├── base_agent.py          # Agent with Claude/OpenAI support
│   ├── mcp_client.py          # MCP server client (SSE transport)
│   └── orchestrator.py        # Multi-agent orchestration
├── services/                   # Business logic
│   ├── subnet_calc.py         # Subnet calculations
│   └── infoblox_client.py     # Infoblox API client
├── frontend-v2/               # Next.js Frontend
│   ├── app/                   # Next.js App Router
│   ├── components/            # React components (sidebar, chat, message)
│   ├── hooks/                 # Custom hooks (useWebSocket)
│   └── lib/                   # Utilities
├── mcp_server.py              # Subnet Calculator MCP server
├── mcp_infoblox.py            # Infoblox DDI MCP server
├── main.py                    # FastAPI backend server
├── mcp_config.json            # MCP & agent configuration
├── test_agent.py              # Test suite
├── FRONTEND.md                # Frontend documentation
└── requirements.txt           # Python dependencies
```

## 🤖 Agent Capabilities

### What Agents Can Do:

1. **Call MCP Tools**:
   - Subnet calculations (calculate, validate CIDR)
   - Infoblox IPAM (list/create subnets, IP spaces, fixed addresses)
   - Infoblox DNS Data (A, CNAME, MX, TXT, PTR records)
   - Infoblox DNS Config (zones, views, DNSSEC)
   - AWS operations (if configured)
   - Terraform management (if configured)

2. **Multi-Agent Delegation**:
   - Agents can call other specialized agents
   - Automatic task routing
   - Collaborative problem solving

3. **Multi-LLM Support**:
   - Different agents can use different LLMs
   - Claude for better tool use
   - OpenAI for different reasoning styles

4. **Smart Formatting**:
   - Markdown rendering with syntax highlighting
   - Automatic chart generation for utilization data
   - User-friendly explanations
   - Visual status indicators (✅, ⚠️, ❌)

## 💡 Example Usage

### In the Web UI:

**Subnet Utilization with Charts:**
```
You: "Show me subnet utilization"

Agent: [Calls Infoblox list_subnets tool]
Agent: Displays table + auto-generates:
       - 📊 Pie chart showing utilization distribution
       - 📈 Bar chart comparing used vs free capacity
```

**DNS Record Creation:**
```
You: "Create A record for www.example.com pointing to 192.168.1.100"

Agent: [Calls create_a_record tool]

Response:
## ✅ DNS Record Created Successfully

**Record Details:**
- Name: `www.example.com`
- Type: A Record
- IP Address: **192.168.1.100**
- Status: Active and propagated

The record is now live and will resolve queries immediately.
```

**Multi-Agent Example:**
```
You: "Provision complete network for new office"

Main Agent: [Delegates to network_specialist]
Network Specialist:
  - Calculates optimal subnets using subnet calculator
  - Creates subnets in Infoblox IPAM
  - Creates DNS zones
  - Configures DHCP
  - Returns summary with visualizations
```

## 🎨 Web UI Features

### Real-Time Communication
- WebSocket connection for instant responses
- Typing indicators while agent is thinking
- Connection status monitoring

### Visual Enhancements
- **Auto-generated charts** from table data
- Pie charts for utilization distribution
- Bar charts for capacity comparison
- Gradient purple theme matching professional UI standards

### User Experience
- Markdown rendering with code syntax highlighting
- Collapsible tool call sections
- Mobile-responsive design
- System status dashboard

## 🧪 Testing

Run the test suite:

```bash
python test_agent.py
```

Test individual components:

```bash
# Test subnet calculator
python test_mcp.py

# Test MCP servers individually
python mcp_server.py          # Subnet calculator on port 3002
python mcp_infoblox.py        # Infoblox DDI on port 3001
```

## 🔐 Security Notes

- Store API keys in `.env` file (never commit!)
- MCP servers run as separate processes with SSE transport
- Infoblox API keys have full tenant access - use carefully
- Review tool permissions before enabling MCP servers
- Implement approval workflows for production changes

## 📚 Documentation

- **README.md**: This file - system overview and setup
- **FRONTEND.md**: Complete Next.js frontend documentation and deployment guide
- **ARCHITECTURE.md**: Complete system architecture and integration patterns
- **CLAUDE.md**: Guidance for Claude Code when working with this repo
- **QUICKSTART.md**: Get running in 5 minutes
- **INFOBLOX_SETUP.md**: Infoblox integration setup guide
- **TECHNOLOGY_STACK.md**: Complete list of technologies and tools
- **mcp_config.json**: All MCP server and agent configurations

## 🐛 Troubleshooting

**"API key not found"**:
- Ensure `.env` file exists and contains your API keys
- Restart all servers after updating `.env`

**"Failed to connect to MCP server"**:
- Ensure MCP servers are running (check terminals)
- Verify servers are on correct ports (3001, 3002)
- Check `mcp_config.json` has correct URLs

**"WebSocket connection failed"**:
- Ensure web_server.py is running on port 8000
- Check browser console for errors
- Try refreshing the page

**"Charts not showing"**:
- Ensure data is formatted as markdown table
- Tables must have "Utilization %" or "%" columns
- Check browser console for JavaScript errors

**"Module not found"**:
- Run `pip install -r requirements.txt`
- Activate virtual environment: `source venv/bin/activate`

## 🔄 System Startup Sequence

1. Start MCP servers first:
   ```bash
   python mcp_infoblox.py    # Port 3001
   python mcp_server.py      # Port 3002
   ```

2. Start web server:
   ```bash
   python web_server.py      # Port 8000
   ```

3. Open browser to `http://localhost:8000`

The web server will automatically connect to running MCP servers on startup.

## 🤝 Contributing

1. Add new MCP servers in `mcp_config.json`
2. Create specialized agents with custom system prompts
3. Extend `base_agent.py` for advanced features
4. Add tests to `test_agent.py`
5. Update documentation

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Built with [FastMCP](https://github.com/jlowin/fastmcp)
- Uses [Anthropic Claude](https://www.anthropic.com/claude) and [OpenAI](https://openai.com)
- Powered by [Model Context Protocol](https://modelcontextprotocol.io)
- Infoblox BloxOne DDI API integration
- FastAPI for modern async web framework
- Chart.js for beautiful data visualizations
- Tailwind CSS for modern UI styling
