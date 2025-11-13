# Integration Guide: How External Systems Connect to Your Platform

This guide explains how other developers/companies can integrate with your AI Agent Platform.

## Two Integration Patterns

### Pattern 1: MCP-to-MCP (Tool Level Integration)
**Use Case**: External agent needs your tools but has their own intelligence/LLM

```
┌─────────────────────────────────────────────────────────────┐
│               EXTERNAL COMPANY'S SYSTEM                      │
│                                                              │
│  ┌────────────────┐                                         │
│  │  Their Agent   │                                         │
│  │  (Claude/GPT)  │                                         │
│  └────────┬───────┘                                         │
│           │                                                  │
│  ┌────────▼────────┐                                        │
│  │ Their MCP Client│                                        │
│  └────────┬────────┘                                        │
└───────────┼─────────────────────────────────────────────────┘
            │
            │ SSE Connection
            │ http://your-domain.com:3000/sse
            │
┌───────────▼─────────────────────────────────────────────────┐
│               YOUR SYSTEM                                    │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          Your MCP Server (Port 3000)                  │  │
│  │                                                        │  │
│  │  Tools:                                                │  │
│  │  - calculate_subnet_info(cidr)                        │  │
│  │  - validate_cidr(cidr)                                │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└──────────────────────────────────────────────────────────────┘

External agent gets: Raw tool execution results
They handle: Intelligence, reasoning, multi-tool orchestration
```

### Pattern 2: API-to-Agent (Intelligence Level Integration)
**Use Case**: External system wants your agent's intelligence + tools

```
┌─────────────────────────────────────────────────────────────┐
│               EXTERNAL COMPANY'S SYSTEM                      │
│                                                              │
│  ┌────────────────────────────────────────┐                │
│  │  Their Application                     │                │
│  │  (Web app, Mobile app, CLI, etc.)      │                │
│  └────────────┬───────────────────────────┘                │
│               │                                              │
│  ┌────────────▼───────────────┐                            │
│  │  HTTP REST Client           │                            │
│  └────────────┬────────────────┘                            │
└───────────────┼─────────────────────────────────────────────┘
                │
                │ HTTPS REST API
                │ POST http://your-domain.com:8000/api/chat
                │ Authorization: Bearer <api-key>
                │
┌───────────────▼─────────────────────────────────────────────┐
│               YOUR SYSTEM                                    │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │       FastAPI Server (Port 8000)                      │  │
│  │                                                        │  │
│  │  Endpoints:                                            │  │
│  │  - POST /api/chat                                     │  │
│  │  - GET  /api/status                                   │  │
│  └────────────────┬─────────────────────────────────────┘  │
│                   │                                          │
│  ┌────────────────▼─────────────────────────────────────┐  │
│  │       Agent Orchestrator                              │  │
│  │       - Manages agents                                │  │
│  │       - Routes requests                               │  │
│  └────────────────┬─────────────────────────────────────┘  │
│                   │                                          │
│  ┌────────────────▼─────────────────────────────────────┐  │
│  │       Your Agent (Claude/OpenAI)                      │  │
│  │       - Natural language understanding               │  │
│  │       - Tool selection & orchestration                │  │
│  │       - Multi-step reasoning                          │  │
│  └────────────────┬─────────────────────────────────────┘  │
│                   │                                          │
│  ┌────────────────▼─────────────────────────────────────┐  │
│  │       MCP Client → MCP Server                         │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└──────────────────────────────────────────────────────────────┘

External system gets: Intelligent responses in natural language
You handle: Intelligence, reasoning, multi-tool orchestration
```

## Comparison Table

| Feature | MCP-to-MCP | API-to-Agent |
|---------|-----------|--------------|
| **What they get** | Raw tool results | Intelligent responses |
| **What they need** | Their own LLM | Just HTTP client |
| **Protocol** | MCP over SSE | REST API |
| **Response format** | JSON tool results | Natural language + metadata |
| **Multi-tool coordination** | They handle it | You handle it |
| **Cost for them** | High (they pay LLM) | Low (you pay LLM) |
| **Latency** | Lower | Slightly higher |
| **Best for** | AI companies with own agents | Any developer/company |

## Example Use Cases

### MCP-to-MCP Examples:

**Company A**: Building AWS deployment agent
- They have Claude agent for deployment logic
- They need subnet calculations
- Solution: Connect to your MCP server
```python
# Their code
await their_mcp_client.connect("http://your-domain.com:3000/sse")
result = await their_mcp_client.call_tool("calculate_subnet_info", {"cidr": "10.0.0.0/16"})
```

**Company B**: Network monitoring SaaS
- They have dashboard showing network topology
- Need subnet validation on user input
- Solution: Connect to your MCP server
```python
# Their code
is_valid = await validate_cidr(user_input)
```

### API-to-Agent Examples:

**Company C**: DevOps automation platform
- No AI/LLM infrastructure
- Want to add "AI Assistant" feature
- Solution: Call your agent API
```python
# Their code
response = requests.post(
    "http://your-domain.com:8000/api/chat",
    json={"message": "Design a VPC with 3 subnets"}
)
print(response.json()["response"])
```

**Company D**: Mobile app for network engineers
- Want chatbot that understands networking
- Solution: Call your agent API
```swift
// Their iOS code
let response = await APIClient.chat(message: "Calculate subnet for 192.168.1.0/24")
```

## Security & Authentication

### For MCP Server (mcp_server.py)

Add authentication middleware:

```python
from fastapi import Header, HTTPException

async def verify_mcp_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing API key")

    token = authorization.split(" ")[1]
    if token not in VALID_API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid API key")

    return token

# Add to MCP server before running
from fastmcp import Context

@mcp.tool()
async def calculate_subnet_info(cidr: str, ctx: Context) -> dict:
    # ctx contains authentication info
    # Access via: ctx.request_context
    ...
```

### For Agent API (api_server.py)

Add API key authentication:

```python
from fastapi import Header, HTTPException

async def verify_api_key(x_api_key: str = Header(None)):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")

    # Check against database or env variable
    if x_api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid API key")

    return x_api_key

@app.post("/api/chat")
async def chat(msg: ChatMessage, api_key: str = Depends(verify_api_key)):
    # api_key is validated
    ...
```

## Rate Limiting

Add rate limiting to prevent abuse:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/chat")
@limiter.limit("10/minute")  # 10 requests per minute per IP
async def chat(request: Request, msg: ChatMessage):
    ...
```

## Monetization Options

If you want to charge for access:

### Option 1: Usage-based pricing
```python
# Track usage per API key
async def track_usage(api_key: str, tool_name: str):
    usage_db.increment(api_key, tool_name)

    # Check if they've exceeded their quota
    if usage_db.get_count(api_key, month=current_month()) > QUOTA:
        raise HTTPException(429, "Quota exceeded")
```

### Option 2: Stripe integration
```python
@app.post("/api/chat")
async def chat(api_key: str = Depends(verify_api_key)):
    # Charge per request
    stripe.Charge.create(
        amount=50,  # $0.50
        currency="usd",
        customer=get_customer_id(api_key)
    )
    ...
```

## Documentation for External Developers

Create an OpenAPI spec:

```python
# api_server.py
app = FastAPI(
    title="AI Agent Platform API",
    description="Intelligent agent with MCP tool integration",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc UI
)
```

Then external developers can visit:
- `http://your-domain.com:8000/docs` - Interactive API docs
- `http://your-domain.com:8000/redoc` - Beautiful documentation
- `http://your-domain.com:8000/openapi.json` - OpenAPI spec

## Testing the Examples

### Test MCP-to-MCP:
```bash
cd examples
python external_mcp_client.py
```

### Test API-to-Agent:
```bash
cd examples
python external_agent_client.py
```

## Production Deployment

For production, you'd deploy:

1. **MCP Server** on port 3000 (or behind API Gateway)
2. **Agent API Server** on port 8000 (or behind API Gateway)
3. **Add authentication** (API keys, OAuth, JWT)
4. **Add rate limiting**
5. **Monitor usage** (DataDog, Prometheus)
6. **Set up billing** (Stripe, AWS Marketplace)

## Complete Integration Flow Diagram

```
External Developer's Perspective:

┌─────────────────────────────────────────────────────────────┐
│  "I want to add subnet calculation to my app"               │
└──────────────┬──────────────────────────────────────────────┘
               │
      ┌────────┴────────┐
      │                 │
      ▼                 ▼
┌─────────────┐   ┌─────────────┐
│ Option 1:   │   │ Option 2:   │
│ Use MCP     │   │ Use Agent   │
│ (Tools)     │   │ (API)       │
└──────┬──────┘   └──────┬──────┘
       │                 │
       ▼                 ▼

┌──────────────────┐  ┌──────────────────┐
│ Install MCP SDK  │  │ Use HTTP client  │
│ Connect to SSE   │  │ Call REST API    │
│ Get raw results  │  │ Get AI response  │
└──────────────────┘  └──────────────────┘

       │                 │
       │                 │
       └────────┬────────┘
                │
                ▼
        Your platform serves
        both integration types!
```

## Summary

You now have TWO products:

1. **MCP Server** (Port 3000)
   - Target: AI engineers with their own agents
   - Value: Specialized tools
   - Pricing: Per tool call or subscription

2. **Agent API** (Port 8000)
   - Target: Any developer
   - Value: Intelligence + tools + orchestration
   - Pricing: Per API call or subscription

Both can run simultaneously and serve different customers!
