# Hey Les! How to Connect Your Agent to Mine

## TL;DR

I've got AI agents running that handle all our Infoblox networking stuff (DNS, IPAM, subnets, etc.). You can connect your agent to mine via a simple REST API - no complicated setup needed.

---

## What You Get

My agents can do **105 different operations**:
- Create/manage DNS records (A, AAAA, CNAME, MX, TXT, PTR, SRV, etc.)
- Handle IPAM (subnets, IP spaces, address allocation)
- Manage DHCP configs
- Calculate subnets
- Security monitoring
- VPN provisioning
- And more...

Basically, anything Infoblox-related, my agents can handle it.

**Note:** We're talking directly to the **Infoblox CSP (Cloud Services Portal) API** (https://csp.infoblox.com), so all this stuff hits the real Infoblox backend. We can talk more about the CSP integration later if you want to know the details or add your own CSP stuff.

---

## Quick Start (Literally 2 Minutes)

### Step 1: Find out what my agents can do

```bash
curl http://MY_SERVER_IP:8000/api/registry
```

(I'll send you the actual server IP separately)

You'll see something like:
```json
{
  "agents": [
    {"name": "main", "description": "General purpose agent"},
    {"name": "network_specialist", "description": "Infoblox expert"}
  ],
  "total_tools": 105
}
```

### Step 2: Send a message to my agent

```bash
curl -X POST http://MY_SERVER_IP:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "List all DNS zones",
    "agent": "network_specialist",
    "from_agent": "les_agent"
  }'
```

That's it! My agent will:
1. Process your request
2. Use whatever tools it needs (DNS API, IPAM, etc.)
3. Send you back a complete answer

---

## The Easy Way (Python)

I made a client library so you don't have to deal with raw HTTP requests.

**Step 1:** Grab this file from me → `a2a_client.py`

**Step 2:** Use it in your code:

```python
from a2a_client import A2AClient

# Connect to my agent system
client = A2AClient(
    base_url="http://MY_SERVER_IP:8000",
    agent_name="les_agent"  # Your agent's name
)

# Ask my agent to do something
response = client.chat(
    message="Create subnet 10.0.0.0/24 for the production network",
    agent="network_specialist"  # Use this one for Infoblox stuff
)

# Check the response
if response['success']:
    print(f"Done! {response['response']}")
    print(f"My agent used {len(response['tool_calls'])} tools to do it")
else:
    print(f"Oops: {response['error']}")
```

That's literally all you need, Les.

---

## What Can You Ask My Agents?

Just send natural language requests like:

**DNS stuff:**
- "List all DNS zones"
- "Create DNS A record for app.example.com pointing to 10.0.0.1"
- "Show me all A records in the infolab.com zone"
- "Delete DNS record with ID abc123"

**IPAM stuff:**
- "Create subnet 192.168.1.0/24 with comment 'Production'"
- "List all IP spaces"
- "Show me available IP addresses in subnet 10.0.0.0/24"
- "Create IPAM host web01.example.com with IP 192.168.1.10"

**Network calculations:**
- "Calculate subnet info for 10.0.0.0/16"
- "Validate CIDR 192.168.1.0/24"

**DHCP:**
- "List all DHCP hardware entries"
- "Show me DHCP option codes"

**Security:**
- "Show me security insights from SOC"
- "List threat named lists"

My agent will figure out what tools to use and get it done.

---

## Example: Build Your Own Agent

Here's a complete working example you can copy/paste:

```python
#!/usr/bin/env python3
"""
Les's agent that talks to my agent
"""

from a2a_client import A2AClient

class LesAgent:
    def __init__(self):
        self.client = A2AClient(
            base_url="http://MY_SERVER_IP:8000",
            agent_name="les_agent"
        )
        print("🤖 Les's agent connected!")

    def do_network_stuff(self):
        # Example 1: Check DNS
        print("\n📋 Checking DNS zones...")
        response = self.client.chat(
            "List all DNS zones in Infoblox",
            agent="network_specialist"
        )

        if response['success']:
            print("✅ Got DNS info!")
            print(response['response'][:200] + "...")  # Show first 200 chars

        # Example 2: Create something
        print("\n🆕 Creating a subnet...")
        response = self.client.chat(
            "Create subnet 10.99.0.0/24 with comment 'Test from Les'",
            agent="network_specialist"
        )

        if response['success']:
            print("✅ Subnet created!")
        else:
            print(f"❌ Failed: {response.get('error')}")

if __name__ == "__main__":
    agent = LesAgent()
    agent.do_network_stuff()
```

Save that, run it, boom - your agent is talking to mine.

---

## The Two Endpoints You Need

### 1. Discovery: `GET /api/registry`

See what agents I have and what they can do.

```bash
curl http://MY_SERVER_IP:8000/api/registry
```

Returns:
```json
{
  "agents": [
    {
      "name": "network_specialist",
      "capabilities": ["subnet-calculator: 2 tools", "infoblox-ddi: 103 tools"]
    }
  ],
  "total_tools": 105
}
```

### 2. Chat: `POST /api/chat`

Send a message/task to my agent.

```bash
curl -X POST http://MY_SERVER_IP:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What you want done",
    "agent": "network_specialist",
    "from_agent": "les_agent"
  }'
```

Returns:
```json
{
  "success": true,
  "response": "Here's what I did...",
  "tool_calls": [{"tool": "create_subnet", "input": {...}}],
  "agent": "network_specialist",
  "to_agent": "les_agent"
}
```

---

## Not Using Python?

No problem! It's just HTTP requests - use whatever you want.

**Node.js:**
```javascript
const axios = require('axios');

const response = await axios.post('http://MY_SERVER_IP:8000/api/chat', {
  message: 'List all DNS zones',
  agent: 'network_specialist',
  from_agent: 'les_agent'
});

console.log(response.data.response);
```

**Go:**
```go
resp, _ := http.Post(
    "http://MY_SERVER_IP:8000/api/chat",
    "application/json",
    bytes.NewBuffer([]byte(`{"message": "List DNS zones", "agent": "network_specialist", "from_agent": "les_agent"}`))
)
```

**Even curl works:**
```bash
curl -X POST http://MY_SERVER_IP:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "List DNS zones", "agent": "network_specialist", "from_agent": "les_agent"}'
```

---

## Which Agent Should You Use?

I've got 2 agents running:

**1. `network_specialist`** ← Use this one for Infoblox stuff
- Knows all about DNS, IPAM, DHCP, networking
- Has access to all 105 tools
- This is probably what you want 99% of the time

**2. `main`** ← General purpose
- Also has access to all 105 tools
- Good for general questions
- Use if you're not sure

Pro tip: Just use `network_specialist` for anything Infoblox-related.

---

## Test Script

Here's a quick test to make sure everything works:

```python
#!/usr/bin/env python3
"""
Quick test for Les to verify connection
"""
import requests

BASE = "http://MY_SERVER_IP:8000"

print("🧪 Les's connection test...")

# Test 1: Can we reach it?
try:
    r = requests.get(f"{BASE}/api/registry", timeout=5)
    print(f"✅ Connected! Found {len(r.json()['agents'])} agents")
except Exception as e:
    print(f"❌ Can't reach server: {e}")
    exit(1)

# Test 2: Can we chat?
try:
    r = requests.post(f"{BASE}/api/chat", json={
        "message": "What can you do?",
        "agent": "network_specialist",
        "from_agent": "les_agent"
    }, timeout=30)

    if r.json()['success']:
        print("✅ Chat works!")
        print(f"Response: {r.json()['response'][:100]}...")
    else:
        print(f"❌ Chat failed: {r.json().get('error')}")
except Exception as e:
    print(f"❌ Request failed: {e}")
    exit(1)

print("\n🎉 All good! You're connected.")
```

---

## Files I'm Sending You

1. **a2a_client.py** - The Python client library (makes your life easier)
2. **This doc** - What you're reading now
3. **The server IP** - I'll send this separately

That's all you need!

---

## Important Notes

⚠️ **No authentication right now** - This is just for us to test/develop. When we go to production, we'll add API keys or whatever.

⏱️ **Response time:** Usually 2-10 seconds depending on what you ask for (the agent has to think and call tools)

🔧 **If something breaks:**
- Check the server IP is right
- Make sure you're using "network_specialist" or "main" for the agent name
- Hit me up and I'll check the logs

---

## What's Actually Happening Behind the Scenes

When you send a message to my agent:

1. Your code → HTTP request → My web server
2. My web server → Passes to orchestrator
3. Orchestrator → Sends to the right agent (main or network_specialist)
4. Agent → Figures out what tools to use (DNS API, IPAM API, etc.)
5. Agent → Calls those tools on Infoblox
6. Agent → Gets results back
7. Agent → Writes a nice summary
8. Response → Comes back to you with the answer + what tools were used

You don't have to worry about any of that - just send messages and get responses.

---

## Advanced: Agent Swarm (If You Want to Get Fancy)

The client library also supports coordinating multiple requests:

```python
from a2a_client import AgentSwarm

swarm = AgentSwarm("http://MY_SERVER_IP:8000")

# Send the same message to all my agents
responses = swarm.broadcast("What's your status?")

# Send different tasks in parallel
tasks = [
    {"message": "List DNS zones", "agent": "network_specialist"},
    {"message": "List IP spaces", "agent": "network_specialist"}
]
results = swarm.parallel_delegate(tasks)
```

But honestly, you probably don't need this unless you're building something complex.

---

## Questions?

Just hit me up. I can:
- Check the logs if something's not working
- Add more capabilities if you need them
- Help debug your integration
- Whatever

The whole point of this is to make it easy for your agent to use my agent's tools without you having to deal with Infoblox APIs directly.

---

## Let's Test It

Once you've got the files:

1. Run the test script above
2. Try a simple request: "List all DNS zones"
3. If it works, try something more complex
4. Let me know if you hit any issues

**That's it, Les!** Should take you like 5 minutes to get connected.

🚀
