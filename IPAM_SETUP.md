## IPAM MCP Server Setup Guide

This guide explains how to add IPAM (IP Address Management) capabilities to your AI Agent Platform using Infoblox Universal DDI / BloxOne IPAM.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    YOUR AI AGENT PLATFORM                        │
│                                                                  │
│  ┌──────────────┐         ┌──────────────┐         ┌─────────┐│
│  │   Subnet     │         │    IPAM      │         │ Context7││
│  │   MCP        │         │    MCP       │         │   MCP   ││
│  │  (Port 3000) │         │  (Port 3001) │         │ (Docs)  ││
│  └──────┬───────┘         └──────┬───────┘         └────┬────┘│
│         │                        │                       │     │
│         │ Local                  │ HTTP REST            │     │
│         │ Calculations           │ to Infoblox          │     │
│         │                        │                       │     │
└─────────┼────────────────────────┼───────────────────────┼─────┘
          │                        │                       │
          ▼                        ▼                       ▼
   ┌──────────────┐        ┌──────────────┐       ┌──────────┐
   │   services/  │        │  Infoblox    │       │ Context7 │
   │ subnet_calc  │        │  BloxOne     │       │  API     │
   │   .py        │        │   Cloud      │       │(Upstash) │
   └──────────────┘        └──────────────┘       └──────────┘
```

## What You Get

### Two Complementary MCP Servers:

**1. Subnet Calculator MCP (Port 3000)**
- **Purpose**: Local subnet calculations
- **No external dependencies**
- **Tools**:
  - `calculate_subnet_info(cidr)` - Math-based calculations
  - `validate_cidr(cidr)` - Validation only
- **Use when**: You need quick calculations without querying IPAM

**2. IPAM MCP (Port 3001)**
- **Purpose**: Live IPAM data from Infoblox
- **Requires**: Infoblox API key
- **Tools**:
  - `list_subnets()` - Get real allocated subnets
  - `get_subnet_info(cidr)` - Get subnet from IPAM with allocation data
  - `check_ip_address(ip)` - Check if IP is allocated, who owns it
  - `get_utilization(cidr)` - Real utilization metrics
  - `find_containing_subnet(ip)` - Which subnet contains this IP
  - `list_ip_spaces()` - List all IP spaces/tenants
  - `find_available_subnets(size)` - Find subnets with capacity
  - `search_subnets(cidr, tag)` - Search by criteria
- **Use when**: You need actual IPAM data, allocation status, or utilization

**3. Context7 MCP (Optional)**
- **Purpose**: Fetch Infoblox API docs for your agent
- **Use when**: Your agent needs to learn Infoblox API on-the-fly

## Setup Steps

### Step 1: Get Infoblox API Key

1. Go to [Infoblox Cloud Services Portal](https://csp.infoblox.com/)
2. Log in to your account
3. Navigate to **User Profile** → **API Keys**
4. Click **Create API Key**
5. Copy the generated key

### Step 2: Configure Environment

Edit `.env` file:

```bash
# IPAM Configuration
IPAM_BASE_URL=https://csp.infoblox.com/api/ddi/v1
IPAM_API_KEY=your-actual-api-key-here
```

For other IPAM systems, adjust the `IPAM_BASE_URL`:
- **Infoblox NIOS WAPI**: `https://your-grid-master/wapi/v2.12`
- **Other IPAM**: Adjust `services/ipam_client.py` accordingly

### Step 3: Start IPAM MCP Server

```bash
# Terminal 1: Subnet Calculator MCP (already running)
python mcp_server.py

# Terminal 2: IPAM MCP (new)
python ipam_mcp_server.py
```

You should see:
```
╭──────────────────────────────────────────────────────────────────╮
│                    IPAM Management                                │
│                                                                   │
│  📦 Transport:   SSE                                              │
│  🔗 Server URL:  http://127.0.0.1:3001/sse                        │
╰──────────────────────────────────────────────────────────────────╯
```

### Step 4: Update Agent API to Use IPAM MCP

Edit `api_server.py`:

```python
await orchestrator.initialize(
    mcp_servers=[
        {
            "name": "subnet",
            "url": "http://localhost:3000/sse"
        },
        {
            "name": "ipam",
            "url": "http://localhost:3001/sse"
        }
    ],
    agent_configs=[
        {"name": "main", "llm_provider": os.getenv("DEFAULT_LLM", "claude")}
    ]
)
```

### Step 5: Restart API Server

```bash
# Terminal 3: API Server
python api_server.py
```

## Usage Examples

### Example 1: Agent Using Both MCPs

```
User: "Is 192.168.1.0/24 allocated in our IPAM?"

Agent thinks:
1. Uses ipam__get_subnet_info("192.168.1.0/24")
   → Gets real IPAM data
2. If found, uses subnet__calculate_subnet_info("192.168.1.0/24")
   → Gets theoretical capacity
3. Compares: "Subnet exists, 45% utilized, 137 IPs available"
```

### Example 2: Find Available Space

```
User: "I need a /24 subnet for a new project"

Agent:
1. Calls ipam__find_available_subnets(24)
   → Gets list of /24s with <80% utilization
2. Calls ipam__get_utilization() for top candidates
3. Recommends: "10.5.42.0/24 is available with only 10% utilization"
```

### Example 3: IP Conflict Detection

```
User: "Can I use 10.0.5.100 for my new server?"

Agent:
1. Calls ipam__check_ip_address("10.0.5.100")
   → Status: "allocated"
   → Usage: "web-server-01.prod.company.com"
2. Responds: "No, that IP is already allocated to web-server-01"
3. Calls ipam__find_containing_subnet("10.0.5.100")
4. Calls ipam__get_utilization() for that subnet
5. Suggests: "Use 10.0.5.150 instead (available in same subnet)"
```

## Using Context7 for Documentation

Context7 MCP can fetch Infoblox API documentation on-demand:

### Option A: Use Context7 as Separate MCP

```bash
# Install Context7 MCP
npx -y @upstash/context7-mcp init

# Start Context7 MCP Server
# (Follow Context7 setup instructions)
```

Add to your agent config:
```python
mcp_servers=[
    {"name": "subnet", "url": "http://localhost:3000/sse"},
    {"name": "ipam", "url": "http://localhost:3001/sse"},
    {"name": "context7", "url": "http://localhost:3002/sse"}
]
```

Your agent can now ask Context7:
```
Agent → context7__search("Infoblox BloxOne API authentication")
       → Gets latest docs
       → Uses docs to make better API calls
```

### Option B: Pre-fetch Docs into Agent System Prompt

```python
# Add to agent's system prompt:
"""
You have access to IPAM MCP which connects to Infoblox BloxOne API.

Infoblox API Authentication:
- Uses Bearer token in Authorization header
- Format: "Authorization: Token YOUR-API-KEY"
- Base URL: https://csp.infoblox.com/api/ddi/v1

Key Endpoints:
- GET /ipam/subnet - List subnets
- GET /ipam/address - List IP addresses
- POST /ipam/address - Allocate new IP
- GET /ipam/ip_space - List IP spaces

Error Handling:
- 401: Invalid/expired API key
- 404: Resource not found
- 429: Rate limit exceeded
"""
```

## Architecture Comparison

### Scenario 1: Only Subnet MCP
```
User → Agent → Subnet MCP → Pure Math Calculation
Fast ✓ | No IPAM Data ✗ | Works Offline ✓
```

### Scenario 2: Only IPAM MCP
```
User → Agent → IPAM MCP → Infoblox API → Real IPAM Data
Slower ✓ | Real Data ✓ | Requires Auth ✓ | Network Dependency ✓
```

### Scenario 3: Both MCPs (Recommended)
```
User → Agent → Chooses Best Tool
           ├→ Subnet MCP (for calculations)
           └→ IPAM MCP (for real data)

Smart Routing ✓ | Best of Both ✓ | Comprehensive ✓
```

### Scenario 4: All Three (Production)
```
User → Agent → Chooses Best Tool
           ├→ Subnet MCP (calculations)
           ├→ IPAM MCP (real data)
           └→ Context7 MCP (when agent needs API docs)

Future-Proof ✓ | Self-Learning Agent ✓ | Handles API Changes ✓
```

## Agent Intelligence Examples

With both MCPs, your agent becomes intelligent:

**Question**: "What's the subnet mask for 10.0.0.0/16?"
- **Agent chooses**: Subnet MCP (calculation only)
- **Why**: No need to query IPAM for pure math

**Question**: "Is 10.0.0.0/16 allocated in production?"
- **Agent chooses**: IPAM MCP
- **Why**: Needs real allocation data

**Question**: "Calculate capacity for our production 10.0.0.0/16 subnet"
- **Agent uses**: BOTH
  1. IPAM MCP → Get real subnet from IPAM
  2. Subnet MCP → Calculate theoretical capacity
  3. Compare → "65,534 theoretical, 45,000 allocated, 20,534 available"

## Multi-Agent Orchestration

Create specialized agents:

```python
agent_configs = [
    {
        "name": "network_planner",
        "llm_provider": "claude",
        "system_prompt": "You plan network architecture using subnet calculations"
        # Uses: Subnet MCP primarily
    },
    {
        "name": "ipam_admin",
        "llm_provider": "openai",
        "system_prompt": "You manage IP allocations in Infoblox IPAM"
        # Uses: IPAM MCP primarily
    },
    {
        "name": "main",
        "llm_provider": "claude",
        "system_prompt": "You coordinate between network planning and IPAM"
        # Uses: Both MCPs + delegates to specialized agents
    }
]
```

Example flow:
```
User: "Plan a new data center network with 5000 servers"

main agent:
  └→ Delegates to network_planner
     └→ Uses subnet__calculate_subnet_info multiple times
     └→ Returns: "Need 2x /21 subnets"

  └→ Delegates to ipam_admin
     └→ Uses ipam__find_available_subnets(21)
     └→ Returns: "Found 10.50.0.0/21 and 10.50.8.0/21"

  └→ main combines both
     └→ Returns comprehensive plan with real available space
```

## Monitoring & Observability

Add logging to track MCP usage:

```python
# In agents/base_agent.py

async def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any]):
    start_time = time.time()

    result = await self.mcp_client.call_tool(...)

    duration = time.time() - start_time

    # Log metrics
    logger.info({
        "tool": tool_name,
        "duration_ms": duration * 1000,
        "input_size": len(str(tool_input)),
        "result_size": len(str(result))
    })
```

Track which MCP gets used most:
- High Subnet MCP usage → Good (fast, local)
- High IPAM MCP usage → Consider caching
- Context7 usage → Agent is learning (good for new APIs)

## Security Best Practices

1. **Never commit API keys**:
   ```bash
   # .gitignore
   .env
   *.key
   ```

2. **Use environment-specific keys**:
   ```bash
   # .env.dev
   IPAM_API_KEY=dev-readonly-key

   # .env.prod
   IPAM_API_KEY=prod-readwrite-key
   ```

3. **Rotate keys regularly**:
   ```bash
   # Monthly key rotation
   0 0 1 * * /usr/local/bin/rotate-ipam-key.sh
   ```

4. **Audit MCP tool calls**:
   ```python
   # Log all IPAM operations
   async def call_tool(...):
       audit_log.write({
           "user": current_user,
           "tool": tool_name,
           "timestamp": now(),
           "input": arguments
       })
   ```

## Troubleshooting

### IPAM MCP Won't Start

**Error**: `ValueError: IPAM API key is required`
```bash
# Check .env file
cat .env | grep IPAM_API_KEY

# Verify it's loaded
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('IPAM_API_KEY'))"
```

### Authentication Fails

**Error**: `401 Unauthorized`
```bash
# Test API key directly
curl -H "Authorization: Token YOUR-KEY" \
  https://csp.infoblox.com/api/ddi/v1/ipam/ip_space

# If fails, regenerate key in Infoblox portal
```

### Agent Doesn't Use IPAM MCP

**Issue**: Agent only uses Subnet MCP

Check agent can see tools:
```bash
curl http://localhost:8000/api/status | jq '.total_tools'
# Should show: 10 tools (2 from subnet + 8 from ipam)
```

If not, check MCP client connection:
```python
# In orchestrator startup
print(f"Connected MCPs: {list(mcp_client.sessions.keys())}")
# Should show: ['subnet', 'ipam']
```

## Summary

You now have:

✅ **Subnet MCP** - Fast local calculations
✅ **IPAM MCP** - Real Infoblox IPAM data
✅ **Context7 Integration** - Self-learning docs
✅ **Multi-agent Orchestration** - Specialized agents
✅ **Production-ready Architecture** - Scalable & secure

Your agent can now:
- Calculate subnets mathematically (Subnet MCP)
- Query real IPAM allocations (IPAM MCP)
- Check IP availability and conflicts
- Find available capacity
- Learn new APIs on-the-fly (Context7)
- Delegate to specialized agents

Next: Add AWS MCP, Terraform MCP, and build complete infrastructure automation!
