# Complete Architecture: Multi-Agent MCP Platform with Infoblox Integration

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   MULTI-AGENT AI PLATFORM WITH INFOBLOX DDI                  │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                      USER INTERFACE                                 │    │
│  │                                                                      │    │
│  │  ┌──────────────────────────────────────────────────────────┐      │    │
│  │  │   Next.js Frontend (Browser)                             │      │    │
│  │  │   - Next.js 14 + TypeScript + shadcn/ui                  │      │    │
│  │  │   - Real-time WebSocket chat                             │      │    │
│  │  │   - Agent selector (main / network_specialist)           │      │    │
│  │  │   - Dark mode with next-themes                           │      │    │
│  │  │   - Markdown rendering (react-markdown)                  │      │    │
│  │  │   - System status dashboard                              │      │    │
│  │  │   - Accessible UI (Radix primitives)                     │      │    │
│  │  │   Port: 3006                                             │      │    │
│  │  └──────────────────────┬───────────────────────────────────┘      │    │
│  └─────────────────────────┼──────────────────────────────────────────┘    │
│                            │                                                │
│                            │ WebSocket + HTTP                               │
│                            │                                                │
│  ┌─────────────────────────▼──────────────────────────────────────────┐   │
│  │              FastAPI + Uvicorn Server (Port 8000)                   │   │
│  │                                                                      │   │
│  │  Endpoints:                                                          │   │
│  │  - WebSocket /ws (Real-time chat)                                   │   │
│  │  - POST /api/upload (File upload)                                   │   │
│  │  - GET  /api/status (System status)                                 │   │
│  │  - GET  /api/agents (Agent list)                                    │   │
│  │  - GET  / (Serve Web UI)                                            │   │
│  └───────────────────────┬──────────────────────────────────────────────┘   │
│                          │                                                  │
│  ┌───────────────────────▼──────────────────────────────────────────────┐  │
│  │              Agent Orchestrator (Singleton)                           │  │
│  │              - Routes WebSocket messages to agents                    │  │
│  │              - Manages agent lifecycle                                │  │
│  │              - Initializes MCP connections                            │  │
│  │              - Coordinates multi-agent workflows                      │  │
│  └────────────────┬─────────────────────────┬────────────────────────────┘  │
│                   │                         │                               │
│       ┌───────────┴────────┐       ┌────────▼──────────┐                   │
│       │                    │       │                    │                   │
│  ┌────▼──────────┐  ┌──────▼──────────────┐  ┌────────▼──────────┐        │
│  │ Agent: main   │  │ Agent: network_     │  │ Agent: (custom)   │        │
│  │ (Claude)      │  │ specialist (Claude) │  │ (Configurable)    │        │
│  │               │  │                     │  │                   │        │
│  │ General AI    │  │ Infoblox Expert     │  │ User-defined      │        │
│  │ with access   │  │ with specialized    │  │ specialized       │        │
│  │ to ALL 50     │◄─┤ prompts for IPAM,   │◄─┤ agents via        │        │
│  │ tools         │  │ DNS, VPN, Security  │  │ mcp_config.json   │        │
│  │               │  │ Federation          │  │                   │        │
│  │ - delegate    │  │ - delegate          │  │ - delegate        │        │
│  │ - mcp tools   │  │ - mcp tools         │  │ - mcp tools       │        │
│  └────┬──────────┘  └──────┬──────────────┘  └─────┬─────────────┘        │
│       │                    │                        │                       │
│       │         All agents share MCP client         │                       │
│       │                    │                        │                       │
│  ┌────▼────────────────────▼────────────────────────▼────────────────┐     │
│  │                MCP Client (Singleton)                              │     │
│  │                - HTTP streamable transport (MCP 2025-06-18)        │     │
│  │                - Multiplexes tool calls from all agents            │     │
│  │                - Handles tool discovery and schema                 │     │
│  │                - 133 tools from 4 servers (SSE backup available)   │     │
│  └────┬─────────────────┬─────────────────┬──────────────────────────┬────┘
│       │                 │                 │                          │
│       │                 │                 │                          │
└───────┼─────────────────┼─────────────────┼──────────────────────────┼────┘
        │                 │                 │                          │
        │ HTTP            │ HTTP            │ HTTP                     │ HTTP
        │                 │                 │                          │
┌───────▼──────┐ ┌────────▼───────┐ ┌───────▼────────┐ ┌─────────────▼─────┐
│  MCP Server  │ │  MCP Server    │ │  MCP Server    │ │  MCP Server       │
│  Infoblox    │ │  Subnet Calc   │ │  AWS Tools     │ │  AWS CloudControl │
│  (4001/mcp)  │ │  (4002/mcp)    │ │  (4003/mcp)    │ │  (4004/mcp)       │
│  (3001/sse)  │ │  (3002/sse)    │ │  (3003/sse)    │ │  (3004/sse)       │
│                      │  │                                                │
│  Tools: 2            │  │  Tools: 48                                     │
│  - calculate_subnet  │  │                                                │
│  - validate_cidr     │  │  **IPAM API (6 tools)**                        │
│                      │  │  - list_ip_spaces                              │
│                      │  │  - list_subnets                                │
│                      │  │  - create_subnet                               │
│                      │  │  - list_ip_addresses                           │
│                      │  │  - reserve_fixed_address                       │
│  Python: services/   │  │                                                │
│  subnet_calc.py      │  │  **DNS Data API (6 tools)**                    │
│                      │  │  - list_dns_records                            │
│                      │  │  - create_a_record                             │
│                      │  │  - create_cname_record                         │
│                      │  │  - create_mx_record                            │
│                      │  │  - create_txt_record                           │
│                      │  │  - delete_dns_record                           │
│                      │  │                                                │
│                      │  │  **DNS Config API (3 tools)**                  │
│                      │  │  - list_dns_zones                              │
│                      │  │  - create_dns_zone                             │
│                      │  │  - list_dns_views                              │
│                      │  │                                                │
│                      │  │  **Federation API (14 tools)**                 │
│                      │  │  Federated Realms:                             │
│                      │  │  - list_federated_realms                       │
│                      │  │  - create_federated_realm                      │
│                      │  │                                                │
│                      │  │  Federated Blocks:                             │
│                      │  │  - list_federated_blocks                       │
│                      │  │  - create_federated_block                      │
│                      │  │  - allocate_next_federated_block               │
│                      │  │                                                │
│                      │  │  Delegations:                                  │
│                      │  │  - list_delegations                            │
│                      │  │  - create_delegation                           │
│                      │  │                                                │
│                      │  │  Overlapping Blocks:                           │
│                      │  │  - list_overlapping_blocks                     │
│                      │  │  - create_overlapping_block                    │
│                      │  │                                                │
│                      │  │  Reserved Blocks:                              │
│                      │  │  - list_reserved_blocks                        │
│                      │  │  - create_reserved_block                       │
│                      │  │                                                │
│                      │  │  Forward Delegations:                          │
│                      │  │  - list_forward_delegations                    │
│                      │  │  - create_forward_delegation                   │
│                      │  │                                                │
│                      │  │  Federated Pools:                              │
│                      │  │  - list_federated_pools                        │
│                      │  │  - create_federated_pool                       │
│                      │  │                                                │
│                      │  │  **NIOSXaaS API (12 tools)**                   │
│                      │  │  Universal Services:                           │
│                      │  │  - list_universal_services                     │
│                      │  │  - create_universal_service                    │
│                      │  │  - get_universal_service                       │
│                      │  │  - update_universal_service                    │
│                      │  │  - delete_universal_service                    │
│                      │  │                                                │
│                      │  │  Endpoints:                                    │
│                      │  │  - list_endpoints                              │
│                      │  │  - create_endpoint                             │
│                      │  │                                                │
│                      │  │  VPN Orchestration:                            │
│                      │  │  - configure_vpn_infrastructure                │
│                      │  │  - get_vpn_endpoint_cnames                     │
│                      │  │  - update_vpn_access_location                  │
│                      │  │  - list_access_locations                       │
│                      │  │  - create_access_location                      │
│                      │  │                                                │
│                      │  │  **Atcfw/DFP API (9 tools)**                   │
│                      │  │  Security Policies:                            │
│                      │  │  - list_security_policies                      │
│                      │  │  - get_security_policy                         │
│                      │  │                                                │
│                      │  │  Threat Intelligence:                          │
│                      │  │  - list_named_lists                            │
│                      │  │  - create_named_list                           │
│                      │  │  - update_named_list                           │
│                      │  │  - delete_named_list                           │
│                      │  │                                                │
│                      │  │  Content Filtering:                            │
│                      │  │  - list_category_filters                       │
│                      │  │  - list_content_categories                     │
│                      │  │  - list_application_filters                    │
│                      │  │                                                │
└──────────────────────┘  │  Python: services/                             │
                          │    - infoblox_client.py (IPAM/DNS/Federation)  │
                          │    - niosxaas_client.py (VPN)                  │
                          │    - atcfw_client.py (Security)                │
                          │  API: https://csp.infoblox.com/api/            │
                          │                                                │
                          └──────────────────┬─────────────────────────────┘
                                             │
                                             │ HTTPS REST
                                             │
                                  ┌──────────▼──────────┐
                                  │  Infoblox BloxOne   │
                                  │  Cloud Platform     │
                                  │  (csp.infoblox.com) │
                                  │                     │
                                  │  - IPAM Management  │
                                  │  - DNS Data         │
                                  │  - DNS Config       │
                                  │  - IPAM Federation  │
                                  │  - NIOSXaaS (VPN)   │
                                  │  - Atcfw/DFP        │
                                  └─────────────────────┘
```

## Integration Points

### 1. Next.js Frontend → FastAPI Backend
**Protocol**: WebSocket (real-time) + HTTP
**Endpoint**: `ws://localhost:8000/ws` (WebSocket), `http://localhost:8000/api/*` (HTTP)
**Purpose**: Real-time bidirectional chat and system status

```typescript
// Custom WebSocket hook (hooks/use-websocket.ts)
const { messages, isConnected, isThinking, sendMessage } = useWebSocket(
  'ws://localhost:8000/ws'
);

// Send message to agent
sendMessage("Calculate subnet for 192.168.1.0/24", "main");

// Fetch system status
const response = await axios.get('http://localhost:8000/api/status');
const status = response.data;
```

### 2. FastAPI Server → Orchestrator → Agents
**Protocol**: In-process Python function calls
**Purpose**: Route WebSocket messages to appropriate agents

```python
# web_server.py
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    while True:
        data = await websocket.receive_text()
        msg_data = json.loads(data)
        message = msg_data.get("message")
        agent_name = msg_data.get("agent", "main")

        # Send thinking status
        await websocket.send_json({"type": "status", "status": "thinking"})

        # Get orchestrator and route to agent
        response = await orchestrator.chat(message, agent_name)

        # Send response
        await websocket.send_json({
            "type": "response",
            "content": response.get("response"),
            "tool_calls": response.get("tool_calls", [])
        })
```

### 3. Agents → MCP Client → MCP Servers
**Protocol**: MCP over SSE (Server-Sent Events)
**Endpoints**:
- `http://127.0.0.1:3001/sse` (Infoblox DDI - 98 tools)
- `http://127.0.0.1:3002/sse` (Subnet Calculator - 2 tools)
- `http://127.0.0.1:3003/sse` (AWS Tools - 20 tools)
- `http://127.0.0.1:3000/sse` (AWS CloudControl - 2 tools)
**Total**: 122 tools from 4 MCP servers

**Purpose**: Agents call tools from MCP servers via shared singleton client

```python
# agents/base_agent.py
result = await self.mcp_client.call_tool(
    server_name="infoblox-ddi",
    tool_name="configure_vpn_infrastructure",
    arguments={
        "service_name": "production-vpn",
        "aws_region": "eu-central-1",
        ...
    }
)
```

### 4. Infoblox MCP Server → Infoblox Cloud
**Protocol**: HTTPS REST API
**Endpoints**:
- `https://csp.infoblox.com/api/ddi/v1/*` (IPAM, DNS, Federation)
- `https://csp.infoblox.com/api/universalinfra/v1/*` (NIOSXaaS VPN)
- `https://csp.infoblox.com/api/atcfw/v1/*` (Atcfw/DFP Security)
**Authentication**: Bearer token (API Key)
**Purpose**: MCP server proxies API calls to Infoblox

```python
# services/infoblox_client.py, niosxaas_client.py, atcfw_client.py
self.session.headers.update({
    "Authorization": f"Token {self.api_key}",
    "Content-Type": "application/json"
})

response = self.session.request("GET",
    f"{self.base_url}/api/ddi/v1/ipam/subnet",
    params={"_limit": 100}
)
```

### 5. Agents → Other Agents (Delegation)
**Protocol**: In-process function calls
**Purpose**: Agent delegation for specialized tasks

```python
# Agent delegation via tool
result = await orchestrator.delegate_to_agent(
    target_agent="network_specialist",
    task="Create DNS zone for new subnet"
)
```

## Data Flow Examples

### Example 1: Simple Subnet Calculation
```
User (Browser) → Types "Calculate 192.168.1.0/24" in Web UI
    ↓ WebSocket message to /ws
FastAPI Server (web_server.py) → Receives WebSocket message
    ↓ Calls orchestrator
Orchestrator → Routes to "main" agent
    ↓
Agent (main) → base_agent.py:chat()
    ↓ Sends to Claude API with tool definitions
Claude LLM → Decides to use calculate_subnet_info
    ↓ Returns function call
Agent → Executes tool via MCP Client
    ↓
MCP Client → mcp_client.py:call_tool()
    ↓ SSE call to http://127.0.0.1:3002/sse
MCP Server (subnet-calculator) → mcp_server.py:calculate_subnet_info()
    ↓ Executes services/subnet_calc.py
Python ipaddress module → Calculates network details
    ↓ Returns {"network": "192.168.1.0", "broadcast": "192.168.1.255", ...}
Result flows back through MCP Client → Agent
    ↓
Agent → Formats response with markdown (## headings, tables, **bold**)
    ↓
WebSocket → Sends JSON response to browser
    ↓
Browser JavaScript → Renders markdown with Marked.js
    ↓
User sees → Beautifully formatted subnet details with table
```

### Example 2: Infoblox IPAM Operation with Chart
```
User (Browser) → "Show me subnet utilization"
    ↓ WebSocket to /ws, agent: "network_specialist"
FastAPI → Routes to network_specialist agent
    ↓
Agent (network_specialist) → Has Infoblox expertise
    ↓ Claude decides to use list_subnets tool
MCP Client → call_tool("infoblox-ddi", "list_subnets")
    ↓ SSE to http://127.0.0.1:3001/sse
MCP Server (infoblox-ddi) → mcp_infoblox.py:list_subnets()
    ↓ Calls services/infoblox_client.py
Infoblox Client → HTTPS GET to https://csp.infoblox.com/api/ddi/v1/ipam/subnet
    ↓ Authorization: Token {api_key}
Infoblox BloxOne → Returns JSON array of subnets with utilization
    ↓
Result → [{address: "10.20.3.0/24", utilization: {"utilization": 1, ...}}, ...]
    ↓ Flows back through MCP
Agent → Formats as markdown table:
        | Subnet | Name | Total IPs | Used | Free | Utilization % |
        |--------|------|-----------|------|------|---------------|
        | 10.20.3.0/24 | ... | 256 | 3 | 253 | 1% |
    ↓
WebSocket → Sends to browser
    ↓
Browser JavaScript → Detects table with "Utilization %" column
    ↓ Automatically triggers generateChartsFromTables()
Chart.js → Creates doughnut chart (proportional utilization)
         → Creates bar chart (used vs free capacity)
    ↓
User sees → Table + Two beautiful interactive charts! 📊📈
```

### Example 3: Complete Network Provisioning with Delegation
```
User → "Provision network for new engineering department with 100 hosts"
    ↓
Agent (main) → Analyzes request, decides multi-step workflow
    ↓
Step 1: Calculate subnet size
Agent (main) → Uses calculate_subnet_info to determine /25 needed (126 hosts)
    ↓
Step 2: Delegate to network specialist
Agent (main) → Delegates to network_specialist
    ↓
Agent (network_specialist) → Takes over
    ↓
Step 3: Create subnet in Infoblox
network_specialist → Calls list_ip_spaces() to get space ID
                  → Calls create_subnet("10.50.0.0/25", space_id, "Engineering Dept")
                  → Infoblox API creates subnet
    ↓
Step 4: Create DNS zone
network_specialist → Calls create_dns_zone("eng.company.com")
                  → Infoblox API creates zone
    ↓
Step 5: Create reverse DNS zone
network_specialist → Calls create_dns_zone("50.10.in-addr.arpa", type="auth")
                  → Infoblox API creates PTR zone
    ↓
Results compile back → network_specialist returns summary
    ↓
Agent (main) → Formats comprehensive report with status icons (✅)
    ↓
User receives → "✅ Network Provisioned Successfully
                 - Subnet: 10.50.0.0/25 (126 usable IPs)
                 - DNS Zone: eng.company.com
                 - Reverse DNS: Configured
                 - Ready for DHCP configuration"
```

### Example 4: File Upload Analysis
```
User → Drags network_diagram.png into chat
    ↓ Browser detects drop event
JavaScript → Calls uploadFile(file)
    ↓ POST /api/upload with FormData
FastAPI → /api/upload endpoint
    ↓ Reads file, determines type (image)
    ↓ Converts to base64
    ↓ Returns {"filename": "...", "content": "base64...", "type": "image"}
Browser → Stores in attachedFiles[]
        → Displays file chip with remove button
User → Types "Analyze this network diagram" + sends
    ↓ WebSocket message includes files array
FastAPI → Prepends file context to message:
          "**Attached Files:**
           **File: network_diagram.png** (52.3 KB, image/png)
           [Image data - 52300 bytes]

           Analyze this network diagram"
    ↓
Agent → Receives message with file context
      → Claude processes image (multimodal)
      → Analyzes diagram and responds
User → Gets analysis of their uploaded network diagram
```

## Scaling Patterns

### Horizontal Scaling
```
                        Load Balancer
                              │
            ┌─────────────────┼─────────────────┐
            │                 │                 │
     ┌──────▼─────┐    ┌──────▼─────┐   ┌──────▼─────┐
     │  FastAPI   │    │  FastAPI   │   │  FastAPI   │
     │  Instance 1│    │  Instance 2│   │  Instance 3│
     └──────┬─────┘    └──────┬─────┘   └──────┬─────┘
            │                 │                 │
            └─────────────────┼─────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
            ┌───────▼──────┐    ┌───────▼──────┐
            │  MCP Server  │    │  MCP Server  │
            │  (Shared)    │    │  (Shared)    │
            └──────────────┘    └──────────────┘
```

### Microservices Pattern
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Agent Service  │     │  Agent Service  │     │  Agent Service  │
│  (Main Agent)   │     │  (Security)     │     │  (DevOps)       │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                       ┌─────────▼─────────┐
                       │   Message Queue   │
                       │   (RabbitMQ)      │
                       └─────────┬─────────┘
                                 │
                    ┌────────────┼────────────┐
                    │            │            │
            ┌───────▼──────┐ ┌───▼──────┐ ┌──▼──────┐
            │ MCP Service  │ │MCP Service│ │MCP Svc  │
            │   (Subnet)   │ │  (AWS)    │ │ (TF)    │
            └──────────────┘ └───────────┘ └─────────┘
```

## Security Layers

```
Internet
   │
   ▼
┌─────────────────────────────────────┐
│   DDoS Protection (Cloudflare)      │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│   WAF (Web Application Firewall)    │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│   API Gateway                        │
│   - Rate Limiting                    │
│   - Authentication (API Keys/JWT)    │
│   - Request Validation               │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│   Load Balancer (ALB)                │
│   - SSL Termination                  │
│   - Health Checks                    │
└─────────────────┬───────────────────┘
                  │
    ┌─────────────┴─────────────┐
    │                           │
┌───▼─────────┐         ┌───────▼──────┐
│  FastAPI    │         │   FastAPI    │
│  (Private   │         │   (Private   │
│   Subnet)   │         │    Subnet)   │
└─────┬───────┘         └───────┬──────┘
      │                         │
      │   Internal Network Only │
      │                         │
┌─────▼─────────────────────────▼──────┐
│       MCP Servers                     │
│       (Private Subnet)                │
│       No Internet Access              │
└───────────────────────────────────────┘
```

## File Structure

```
subnet_mcp/
├── web_server.py                 # FastAPI + WebSocket server (Port 8000)
├── mcp_server.py                 # Subnet Calculator MCP (Port 3002)
├── mcp_infoblox.py               # Infoblox DDI MCP (Port 3001)
├── mcp_config.json               # MCP servers and agent configurations
├── .env                          # API keys (gitignored)
├── .env.example                  # Template for environment variables
│
├── agents/                       # Multi-agent framework
│   ├── orchestrator.py           # Agent coordinator (singleton)
│   ├── base_agent.py             # Agent with Claude/OpenAI + MCP tools
│   └── mcp_client.py             # MCP client (singleton, SSE connections)
│
├── services/                     # Business logic layer
│   ├── subnet_calc.py            # Subnet calculation (Python ipaddress)
│   └── infoblox_client.py        # Infoblox API client (IPAM, DNS, Federation)
│
├── frontend-v2/                 # Next.js Frontend (Port 3006)
│   ├── app/                     # Next.js App Router
│   │   ├── page.tsx            # Main application page
│   │   ├── layout.tsx          # Root layout with ThemeProvider
│   │   └── globals.css         # Tailwind + Infoblox theme
│   ├── components/             # React components
│   │   ├── sidebar.tsx         # System status sidebar
│   │   ├── chat.tsx            # Chat interface
│   │   ├── message.tsx         # Message renderer
│   │   ├── theme-provider.tsx  # Dark mode provider
│   │   └── ui/                 # shadcn/ui components
│   ├── hooks/                  # Custom React hooks
│   │   └── use-websocket.ts    # WebSocket connection hook
│   └── lib/                    # Utilities
│       └── utils.ts            # Helper functions
│
├── Documentation/
│   ├── README.md                 # Project overview and setup
│   ├── ARCHITECTURE.md           # This file - system architecture
│   ├── QUICKSTART.md             # 5-minute setup guide
│   ├── TECHNOLOGY_STACK.md       # Complete tech stack documentation
│   ├── INFOBLOX_SETUP.md         # Infoblox integration guide
│   ├── CLAUDE.md                 # Guide for Claude Code AI assistant
│   └── IPAM_SETUP.md             # Legacy IPAM setup (deprecated)
│
└── requirements.txt              # Python dependencies
```

## Key Design Decisions

### 1. Why Separate MCP Server from Agent API?
- **MCP Server (Port 3000)**: Tool-level access for AI engineers
- **Agent API (Port 8000)**: Intelligence-level access for all developers
- Allows both integration patterns simultaneously

### 2. Why Singleton MCP Client?
- All agents share connections to MCP servers
- Avoids duplicate SSE connections
- Easier connection management

### 3. Why Agent Registry Pattern?
- Enables dynamic agent-to-agent communication
- Fully connected mesh topology
- Each agent can delegate to any other agent

### 4. Why SSE Instead of WebSocket?
- MCP protocol standard uses SSE
- Better for server→client streaming
- Simpler reconnection logic
- Works through more firewalls/proxies

## Summary

You now have a production-ready multi-agent platform with comprehensive cloud infrastructure management:

1. **Next.js Frontend** (Port 3006):
   - Next.js 14 + TypeScript + shadcn/ui
   - Real-time WebSocket chat
   - Dark mode with next-themes
   - System status dashboard
   - Markdown rendering with GitHub Flavored Markdown
   - Accessible UI with Radix primitives
   - Professional component library

2. **Multi-Agent System**:
   - 2 pre-configured agents (main, network_specialist)
   - Agent-to-agent delegation with `delegate` tool
   - All agents share access to **122 tools** from 4 MCP servers
   - Support for Claude and OpenAI LLMs
   - Easy to add custom agents via mcp_config.json

3. **Comprehensive Infoblox Integration** (98 tools):
   - **IPAM API**: IP spaces, subnets, addresses
   - **DNS Data API**: A, CNAME, MX, TXT, PTR records
   - **DNS Config API**: Zones, views, DNSSEC
   - **Federation API**: Multi-tenant IPAM management
   - **NIOSXaaS API**: VPN Universal Service provisioning
   - **Atcfw/DFP API**: DNS Security & Threat Protection
   - Direct REST API integration with Infoblox BloxOne Cloud
   - Bearer token authentication (API Key)

4. **VPN Automation**:
   - End-to-end VPN provisioning from Infoblox NIOSXaaS to AWS
   - Consolidated Configure API for atomic VPN operations
   - Automatic retry logic for 409/429 conflicts
   - Support for AWS VPC VPN gateway configuration

5. **Security & Compliance**:
   - DNS Firewall Protection (Atcfw/DFP)
   - Threat intelligence with custom named lists
   - Content category filtering
   - Security policy management

6. **Infrastructure as Code**:
   - Terraform MCP server integration
   - AWS best practices and security compliance
   - Checkov security scanning

7. **Local Subnet Calculator**:
   - 2 tools for fast offline subnet calculations
   - No external dependencies
   - Python ipaddress module

8. **Production Features**:
   - Singleton MCP client (efficient connection pooling)
   - Scalable FastAPI + Uvicorn architecture
   - Automatic visual data representation
   - Configurable agents and MCP servers
   - Security best practices (API keys in .env)

9. **Total Capabilities**:
   - **50 total tools** from 2 active MCP servers (+ Terraform MCP available)
   - **2 agents** (extensible)
   - **6 Infoblox API services** fully integrated
   - **Real-time** WebSocket communication
   - **Automatic** chart generation
   - **End-to-end VPN automation**
