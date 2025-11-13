# Technology Stack

Complete list of all software, libraries, frameworks, and tools used to build this multi-agent MCP system.

## Table of Contents
- [Core Technologies](#core-technologies)
- [Backend Frameworks](#backend-frameworks)
- [Frontend Technologies](#frontend-technologies)
- [AI/LLM Integration](#aillm-integration)
- [MCP (Model Context Protocol)](#mcp-model-context-protocol)
- [Python Libraries](#python-libraries)
- [Development Tools](#development-tools)
- [APIs & External Services](#apis--external-services)

---

## Core Technologies

### Programming Languages
- **Python 3.10+**: Main programming language for backend, agents, and MCP servers
- **JavaScript (ES6+)**: Frontend interactivity, WebSocket client, chart rendering
- **HTML5**: Web UI structure
- **CSS3**: Styling with modern features (Grid, Flexbox, gradients)

### Runtime Environment
- **Python Virtual Environment (venv)**: Isolated dependency management
- **Node.js** (optional): For npm-based MCP servers (AWS, GitHub, etc.)

---

## Backend Frameworks

### Web Framework
- **FastAPI 0.104.0+**
  - Modern async Python web framework
  - WebSocket support for real-time communication
  - Automatic OpenAPI documentation
  - Type hints and Pydantic validation
  - CORS middleware for cross-origin requests
  - Used in: `web_server.py`

- **Uvicorn 0.24.0+**
  - ASGI server for FastAPI
  - uvloop for high-performance event loop
  - WebSocket support
  - Hot-reload in development
  - Command: `uvicorn[standard]`

### MCP Server Framework
- **FastMCP 2.0.0+**
  - Python framework for building MCP servers
  - SSE (Server-Sent Events) transport
  - Automatic tool discovery and registration
  - Type-safe tool definitions
  - Inspector UI for debugging
  - Used in: `mcp_server.py`, `mcp_infoblox.py`

---

## Frontend Technologies

### UI Framework & Libraries
- **Tailwind CSS 3.x (CDN)**
  - Utility-first CSS framework
  - Custom color configuration (purple gradient theme)
  - Responsive design utilities
  - Used for: Component styling, layout, animations

- **Chart.js 4.4.0 (CDN)**
  - JavaScript charting library
  - Doughnut (pie) charts for utilization overview
  - Stacked bar charts for capacity comparison
  - Responsive and animated
  - Used for: Auto-generating visualizations from table data

- **Marked.js (latest, CDN)**
  - Markdown parser and renderer
  - GitHub-flavored markdown support
  - Code syntax highlighting
  - Used for: Converting agent responses to formatted HTML

### Communication Protocol
- **WebSocket**
  - Real-time bidirectional communication
  - JSON message format
  - Connection state management
  - Auto-reconnection logic
  - Used in: `web_server.py` and `static/index.html`

- **HTTP/HTTPS**
  - REST API endpoints
  - Status monitoring
  - Agent listing
  - Static file serving

---

## AI/LLM Integration

### LLM Providers

#### Anthropic Claude
- **anthropic 0.40.0+**
  - Official Python SDK for Claude API
  - Model: `claude-3-5-sonnet-20241022`
  - Function calling / tool use
  - Streaming responses
  - System prompts
  - Used in: `agents/base_agent.py`

#### OpenAI
- **openai 1.0.0+**
  - Official Python SDK for OpenAI API
  - Model: `gpt-4-turbo-preview`
  - Function calling
  - Chat completions
  - Used in: `agents/base_agent.py` (optional)

### Agent Framework
- **Custom Multi-Agent System**
  - `agents/base_agent.py`: Core agent with LLM + tool integration
  - `agents/orchestrator.py`: Multi-agent coordination
  - `agents/mcp_client.py`: Singleton MCP client for tool access
  - Features:
    - Agent-to-agent delegation
    - Shared MCP tool access
    - Conversation history management
    - Multi-LLM support

---

## MCP (Model Context Protocol)

### MCP SDK
- **mcp 1.2.0+**
  - Official MCP client SDK
  - SSE transport for server communication
  - Tool discovery and execution
  - Schema validation
  - Used in: `agents/mcp_client.py`

### MCP Servers Built

#### 1. Subnet Calculator MCP Server
- **File**: `mcp_server.py`
- **Port**: 3002
- **Transport**: SSE
- **Tools**:
  - `calculate_subnet_info`: Calculate subnet details from CIDR
  - `validate_cidr`: Validate CIDR notation
- **Dependencies**: `services/subnet_calc.py`

#### 2. Infoblox DDI MCP Server
- **File**: `mcp_infoblox.py`
- **Port**: 3001
- **Transport**: SSE
- **Tools** (14 total):
  - **IPAM**: list_ip_spaces, list_subnets, create_subnet, list_ip_addresses, reserve_fixed_address
  - **DNS Data**: list_dns_records, create_a_record, create_cname_record, create_mx_record, create_txt_record, delete_dns_record
  - **DNS Config**: list_dns_zones, create_dns_zone, list_dns_views
- **Dependencies**: `services/infoblox_client.py`

---

## Python Libraries

### Web & HTTP
```python
fastapi>=0.104.0           # Web framework
uvicorn[standard]>=0.24.0  # ASGI server
websockets>=12.0           # WebSocket support
httpx>=0.27.0              # Async HTTP client
requests>=2.31.0           # Sync HTTP client (Infoblox API)
```

### MCP & Agents
```python
fastmcp>=2.0.0             # MCP server framework
mcp>=1.2.0                 # MCP client SDK
anthropic>=0.40.0          # Claude API
openai>=1.0.0              # OpenAI API
```

### Data & Utilities
```python
pydantic>=2.0.0            # Data validation
python-dotenv>=1.0.0       # Environment variables
```

### Network Calculations
```python
ipaddress                  # Built-in Python module for IP operations
```

### Optional (Streamlit Alternative)
```python
streamlit>=1.30.0          # Alternative web UI (app.py)
```

---

## Development Tools

### Package Management
- **pip**: Python package installer
- **requirements.txt**: Dependency specification

### Configuration Management
- **python-dotenv**: Load environment variables from `.env` file
- **JSON**: Configuration files (`mcp_config.json`)

### Code Organization
- **Python Modules**: Organized into `agents/`, `services/`, `static/`
- **Environment Variables**: `.env` file for secrets
- **Configuration**: `mcp_config.json` for system setup

### Testing
- **Custom Test Suite**: `test_agent.py`
- **Manual Testing**: Individual component testing

---

## APIs & External Services

### Infoblox BloxOne DDI API
- **Base URL**: https://csp.infoblox.com
- **Authentication**: API Key (Bearer token)
- **APIs Used**:
  - **IPAM Service**: `/api/ddi/v1/ipam/`
  - **DNS Data Service**: `/api/ddi/v1/dns/record`
  - **DNS Config Service**: `/api/ddi/v1/dns/`
- **Features**:
  - IP address management
  - Subnet provisioning
  - DNS record management (A, AAAA, CNAME, MX, TXT, PTR, SRV)
  - DNS zone management
  - DNSSEC configuration

### Anthropic Claude API
- **Endpoint**: https://api.anthropic.com
- **Model**: claude-3-5-sonnet-20241022
- **Features**: Function calling, streaming, system prompts

### OpenAI API (Optional)
- **Endpoint**: https://api.openai.com
- **Model**: gpt-4-turbo-preview
- **Features**: Chat completions, function calling

---

## Architecture Patterns

### Communication Protocols
1. **HTTP REST**: Browser ↔ FastAPI server
2. **WebSocket**: Real-time chat communication
3. **SSE (Server-Sent Events)**: MCP client ↔ MCP servers
4. **In-Process**: Agent ↔ Agent delegation

### Design Patterns
- **Singleton Pattern**: MCP client shared across agents
- **Factory Pattern**: Agent creation in orchestrator
- **Observer Pattern**: WebSocket message handling
- **Adapter Pattern**: LLM provider abstraction

### Architectural Styles
- **Microservices**: Separate MCP servers as independent services
- **Event-Driven**: WebSocket for real-time events
- **Client-Server**: Web UI ↔ Backend API
- **Multi-Agent System**: Collaborative AI agents

---

## File Structure

```
subnet_mcp/
├── agents/
│   ├── base_agent.py          # Agent with LLM integration
│   ├── mcp_client.py          # MCP client (singleton)
│   └── orchestrator.py        # Multi-agent coordinator
├── services/
│   ├── subnet_calc.py         # Subnet calculation logic
│   └── infoblox_client.py     # Infoblox API wrapper
├── static/
│   └── index.html             # Web UI (HTML/CSS/JS)
├── mcp_server.py              # Subnet calculator MCP server
├── mcp_infoblox.py            # Infoblox DDI MCP server
├── web_server.py              # FastAPI + WebSocket server
├── mcp_config.json            # System configuration
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (secret)
├── .env.example               # Environment template
└── *.md                       # Documentation
```

---

## CDN Resources

### JavaScript Libraries (Loaded from CDN)
```html
<!-- Tailwind CSS -->
<script src="https://cdn.tailwindcss.com"></script>

<!-- Chart.js for visualizations -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js"></script>

<!-- Marked.js for markdown rendering -->
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
```

### Fonts
```css
/* Google Fonts - Inter -->
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
```

---

## System Requirements

### Minimum Requirements
- **Python**: 3.10 or higher
- **RAM**: 2GB minimum (4GB recommended)
- **Disk Space**: 500MB for dependencies
- **Network**: Internet access for API calls

### Recommended Setup
- **OS**: macOS, Linux, or Windows with WSL
- **CPU**: Multi-core for parallel MCP servers
- **Browser**: Modern browser (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)

---

## Performance Characteristics

### Response Times
- **WebSocket Latency**: < 50ms local
- **LLM API Calls**: 1-5 seconds (varies by model)
- **MCP Tool Calls**: < 100ms (local), 200-500ms (API)
- **Chart Rendering**: < 100ms for typical datasets

### Scalability
- **Concurrent Users**: FastAPI supports thousands with async
- **Agent Instances**: Limited by API rate limits
- **MCP Servers**: Can run distributed across multiple machines

---

## Security Features

### Authentication & Authorization
- **API Keys**: Stored in `.env` (never committed)
- **CORS**: Configured in FastAPI middleware
- **Environment Isolation**: Python virtual environment

### Data Protection
- **No Data Storage**: Stateless agents (conversation in-memory only)
- **HTTPS**: Recommended for production
- **API Key Rotation**: Supported via `.env` update

---

## Deployment Considerations

### Development
- Run locally with `python web_server.py`
- Multiple terminals for MCP servers
- Hot-reload supported in Uvicorn

### Production (Recommendations)
- **Process Manager**: systemd, supervisor, or PM2
- **Reverse Proxy**: nginx or Caddy
- **SSL/TLS**: Let's Encrypt certificates
- **Monitoring**: Prometheus + Grafana
- **Logging**: Structured JSON logs
- **Rate Limiting**: API gateway (e.g., Kong, AWS API Gateway)

---

## Version Control

### Git Configuration
```gitignore
.env                 # Secrets never committed
venv/               # Virtual environment excluded
__pycache__/        # Python bytecode excluded
*.pyc               # Compiled Python excluded
.DS_Store           # macOS files excluded
```

---

## Summary

This system is built with modern, production-ready technologies:

**Frontend**: HTML5 + Tailwind CSS + Chart.js + WebSocket + Vanilla JavaScript
**Backend**: Python 3.10+ + FastAPI + Uvicorn + WebSocket
**AI Layer**: Anthropic Claude + OpenAI + Custom Multi-Agent Framework
**MCP Layer**: FastMCP + MCP SDK + SSE Transport
**APIs**: Infoblox BloxOne DDI (IPAM, DNS Data, DNS Config)
**DevOps**: python-dotenv + requirements.txt + JSON config

**Total Stack Complexity**: Medium (well-organized, maintainable)
**Total Dependencies**: ~20 Python packages + 3 CDN libraries
**Learning Curve**: Intermediate (requires understanding of async Python, AI agents, MCP protocol)
