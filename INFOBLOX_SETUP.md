# Infoblox BloxOne DDI Integration Setup

This guide helps you set up the Infoblox BloxOne DDI integration with your multi-agent system.

## What's Integrated

Your system now has access to **7 Infoblox API services** with **57 total tools**:

### 1. IPAM API (IP Address Management) - 6 Tools
- `list_ip_spaces` - List IP spaces/tenants
- `list_subnets` - List subnets with filters (address, space)
- `create_subnet` - Create new subnet with DHCP configuration
- `list_ip_addresses` - List IP addresses and allocation state
- `reserve_fixed_address` - Reserve fixed IP for DHCP

### 2. DNS Data API (DNS Records) - 6 Tools
- `list_dns_records` - List and filter DNS records
- `create_a_record` - Create A record (IPv4)
- `create_cname_record` - Create CNAME (alias)
- `create_mx_record` - Create MX (mail exchanger)
- `create_txt_record` - Create TXT record (SPF, DKIM, DMARC, verification)
- `delete_dns_record` - Delete DNS record (moves to recycle bin)

### 3. DNS Config API (DNS Infrastructure) - 3 Tools
- `list_dns_zones` - List authoritative and forward zones
- `create_dns_zone` - Create new DNS zone (auth or forward)
- `list_dns_views` - List DNS views

### 4. IPAM Federation API (Multi-Tenant IPAM) - 14 Tools

Advanced multi-tenant IP address management capabilities:

**Federated Realms (2 tools):**
- `list_federated_realms` - List federation realms
- `create_federated_realm` - Create new federation realm

**Federated Blocks (3 tools):**
- `list_federated_blocks` - List federated IP blocks
- `create_federated_block` - Create federated block
- `allocate_next_federated_block` - Auto-allocate next available block

**Delegations (2 tools):**
- `list_delegations` - List IP block delegations
- `create_delegation` - Delegate IP block to tenant/organization

**Overlapping Blocks (2 tools):**
- `list_overlapping_blocks` - List overlapping IP blocks
- `create_overlapping_block` - Create overlapping block

**Reserved Blocks (2 tools):**
- `list_reserved_blocks` - List reserved IP blocks
- `create_reserved_block` - Reserve IP block for future use

**Forward Delegations (2 tools):**
- `list_forward_delegations` - List forward-looking delegations
- `create_forward_delegation` - Create future delegation

**Federated Pools (2 tools):**
- `list_federated_pools` - List federated IP pools
- `create_federated_pool` - Create federated pool

### 5. NIOSXaaS API (VPN Universal Service) - 12 Tools

**New!** VPN provisioning and management capabilities:

**Universal Services (5 tools):**
- `list_universal_services` - List all VPN universal services
- `create_universal_service` - Create new universal service
- `get_universal_service` - Get universal service details by ID
- `update_universal_service` - Update universal service configuration
- `delete_universal_service` - Delete universal service

**Endpoints (2 tools):**
- `list_endpoints` - List all VPN endpoints
- `create_endpoint` - Create new VPN endpoint

**VPN Orchestration (5 tools):**
- `configure_vpn_infrastructure` - **Atomic VPN provisioning** (consolidated API)
- `get_vpn_endpoint_cnames` - Get endpoint CNAMEs for AWS Customer Gateway
- `update_vpn_access_location` - Update access location with tunnel IPs
- `list_access_locations` - List all VPN access locations
- `create_access_location` - Create new access location

### 6. Atcfw/DFP API (DNS Security & Threat Protection) - 9 Tools

**New!** DNS Firewall Protection and threat intelligence:

**Security Policies (2 tools):**
- `list_security_policies` - List all DNS security policies
- `get_security_policy` - Get security policy details by ID

**Threat Intelligence (4 tools):**
- `list_named_lists` - List custom threat intelligence lists
- `create_named_list` - Create custom named list (domains, IPs, etc.)
- `update_named_list` - Update named list items
- `delete_named_list` - Delete named list

**Content Filtering (3 tools):**
- `list_category_filters` - List content category filters
- `list_content_categories` - List available content categories
- `list_application_filters` - List application-based filters

### 7. SOC Insights API (Security Operations Center) - 11 Tools

**New!** Threat monitoring, incident response, and policy compliance:

**Security Insights (7 tools):**
- `list_security_insights` - List security insights with filters (status, threat_type, priority)
- `get_security_insight_details` - Get detailed information for a specific security insight
- `update_security_insight_status` - Update insight status (IN_PROGRESS, RESOLVED, CLOSED, FALSE_POSITIVE)
- `get_insight_threat_indicators` - Get IOCs (Indicators of Compromise) for an insight
- `get_insight_security_events` - Get security events associated with an insight
- `get_insight_affected_assets` - Get affected devices, IPs, and MAC addresses
- `get_insight_comments_history` - Get historical comments and status changes

**Policy Compliance (3 tools):**
- `list_policy_analytics_insights` - List policy analytics insights for configuration compliance
- `get_policy_analytics_insight_details` - Get detailed policy analytics insight
- `list_policy_compliance_insights` - List policy compliance check insights

## Setup Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Infoblox API Key

1. Log in to [Infoblox Cloud Services Portal](https://csp.infoblox.com)
2. Go to **User Profile** → **API Keys**
3. Click **Create API Key**
4. Copy the generated API key

### 3. Configure Environment

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and add your credentials:
```bash
# Infoblox Configuration
INFOBLOX_API_KEY=your_actual_api_key_here
INFOBLOX_BASE_URL=https://csp.infoblox.com

# LLM API Keys (at least one required)
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here
```

### 4. Verify Configuration

Check that the Infoblox MCP server is enabled in `mcp_config.json`:

```json
{
  "mcpServers": {
    "infoblox-ddi": {
      "enabled": true,
      ...
    }
  }
}
```

### 5. Launch the System

You need 3 terminal windows:

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

**Terminal 3 - Web Server:**
```bash
source venv/bin/activate
python web_server.py
```

The system will:
1. Both MCP servers start and listen for SSE connections
2. Web server connects to MCP servers
3. Discovers 59 total tools (2 from subnet-calculator, 57 from infoblox-ddi)
4. Initializes 2 agents (main + network_specialist)
5. Web UI available at http://localhost:8000

## Using Infoblox Tools

### Available Agents

- **main**: General-purpose agent with access to all tools
- **network_specialist**: Expert in IPAM, DNS, and DHCP with Infoblox

Select the agent from the dropdown in the UI.

### Example Queries

#### IPAM Operations
```
"List all IP spaces"
"Show me subnets in the 10.0.0.0/8 range"
"Create a /24 subnet at 192.168.50.0 in space ipam/ip_space/abc123"
"Reserve IP address 10.0.1.100 for the file server"
"Find available IP addresses in subnet 172.16.0.0/24"
```

#### DNS Data Operations
```
"Create an A record for webserver pointing to 192.168.1.100 in zone dns/auth_zone/xyz"
"List all A records in my DNS"
"Create a CNAME for blog pointing to www.example.com"
"Add MX record for mail.example.com with priority 10"
"Create TXT record for SPF: v=spf1 include:_spf.google.com ~all"
```

#### DNS Config Operations
```
"List all DNS zones"
"Create an authoritative zone for example.com"
"Show me DNS views"
"Create a forward zone for internal.local"
```

#### VPN Operations
```
"Provision VPN infrastructure for connecting AWS VPC to Infoblox"
"List all universal services"
"Get VPN endpoint CNAMEs for AWS Customer Gateway configuration"
"Update access location with AWS tunnel IPs after VPN creation"
```

#### Security Operations
```
"List all DNS security policies"
"Create a custom threat intelligence list for blocking malicious domains"
"Show me available content filtering categories"
"List application filters"
```

#### Hybrid Workflows
```
"I need to provision a new /24 network for the engineering team"
(Agent will: validate CIDR → create subnet → configure DHCP → create DNS zone → create PTR zone)

"Set up DNS for web server at 10.0.1.50 named web01.prod.company.com"
(Agent will: create forward A record → create reverse PTR record → verify)

"Provision end-to-end VPN from Infoblox NIOSXaaS to AWS VPC"
(Agent will: create universal service → create endpoint → get CNAMEs → configure AWS VPN → update access location with tunnel IPs)
```

## Tools Reference

### IPAM Tools (6)
- `list_ip_spaces` - List IP spaces
- `list_subnets` - List subnets with filters
- `create_subnet` - Create new subnet
- `list_ip_addresses` - List IP addresses and their state
- `reserve_fixed_address` - Reserve IP for DHCP

### DNS Data Tools (6)
- `list_dns_records` - List DNS records with filters
- `create_a_record` - Create A record (IPv4)
- `create_cname_record` - Create CNAME (alias)
- `create_mx_record` - Create MX (mail)
- `create_txt_record` - Create TXT record
- `delete_dns_record` - Delete DNS record

### DNS Config Tools (3)
- `list_dns_zones` - List zones (auth/forward)
- `create_dns_zone` - Create new zone
- `list_dns_views` - List DNS views

### Federation Tools (14)
- `list_federated_realms` / `create_federated_realm`
- `list_federated_blocks` / `create_federated_block` / `allocate_next_federated_block`
- `list_delegations` / `create_delegation`
- `list_overlapping_blocks` / `create_overlapping_block`
- `list_reserved_blocks` / `create_reserved_block`
- `list_forward_delegations` / `create_forward_delegation`
- `list_federated_pools` / `create_federated_pool`

### NIOSXaaS VPN Tools (12)
- `list_universal_services` / `create_universal_service` / `get_universal_service` / `update_universal_service` / `delete_universal_service`
- `list_endpoints` / `create_endpoint`
- `configure_vpn_infrastructure` (atomic operation with consolidated API)
- `get_vpn_endpoint_cnames` (for AWS Customer Gateway)
- `update_vpn_access_location` (add tunnel IPs after VPN creation)
- `list_access_locations` / `create_access_location`

### Atcfw/DFP Security Tools (9)
- `list_security_policies` / `get_security_policy`
- `list_named_lists` / `create_named_list` / `update_named_list` / `delete_named_list`
- `list_category_filters` / `list_content_categories` / `list_application_filters`

## Architecture

```
┌──────────────────────────────────────────────┐
│    Web UI (Browser) - Port 8000              │
│    - WebSocket chat                          │
│    - Chart.js visualizations                 │
│    - File upload (drag & drop)               │
└──────────────┬───────────────────────────────┘
               │ WebSocket + HTTP
┌──────────────▼───────────────────────────────┐
│   FastAPI + Uvicorn (web_server.py)          │
│   - WebSocket /ws                            │
│   - POST /api/upload                         │
│   - GET /api/status                          │
└──────────────┬───────────────────────────────┘
               │
┌──────────────▼───────────────────────────────┐
│   Orchestrator (Multi-Agent)                 │
│   - main agent (Claude)                      │
│   - network_specialist agent (Claude)        │
└──────┬─────────────────┬─────────────────────┘
       │                 │
       │ SSE             │ SSE
       │                 │
┌──────▼──────┐   ┌──────▼────────────────────────────────┐
│ Subnet Calc │   │ Infoblox MCP Server                   │
│ MCP Server  │   │ (mcp_infoblox.py)                     │
│             │   │                                       │
│ Port: 3002  │   │ Port: 3001                            │
│ Tools: 2    │   │ Tools: 57                             │
└─────────────┘   │                                       │
                  │ API Groups:                           │
                  │ - IPAM (6 tools)                      │
                  │ - DNS Data (6 tools)                  │
                  │ - DNS Config (3 tools)                │
                  │ - Federation (14 tools)               │
                  │ - NIOSXaaS VPN (12 tools)             │
                  │ - Atcfw/DFP Security (9 tools)        │
                  │                                       │
                  │ services/                             │
                  │  - infoblox_client.py (IPAM/DNS/Fed)  │
                  │  - niosxaas_client.py (VPN)           │
                  │  - atcfw_client.py (Security)         │
                  └─────────┬─────────────────────────────┘
                            │ HTTPS REST
                            │ (Bearer Token Auth)
                  ┌─────────▼─────────────────────────────┐
                  │ Infoblox BloxOne Cloud                │
                  │ (csp.infoblox.com)                    │
                  │                                       │
                  │ APIs:                                 │
                  │ - /api/ddi/v1/ipam/*                  │
                  │ - /api/ddi/v1/dns/*                   │
                  │ - /api/ddi/v1/federation/*            │
                  │ - /api/universalinfra/v1/* (VPN)      │
                  │ - /api/atcfw/v1/* (Security)          │
                  └───────────────────────────────────────┘
```

## Troubleshooting

### "Infoblox client not initialized"
- Check that `INFOBLOX_API_KEY` is set in `.env`
- Verify the API key is valid in Infoblox portal
- Restart the Streamlit app

### "HTTP 401 Unauthorized"
- API key is invalid or expired
- Generate a new API key in Infoblox portal

### "HTTP 403 Forbidden"
- Your account doesn't have permissions
- Contact Infoblox admin to grant API access

### MCP server not starting
- Check `mcp_config.json` has `"enabled": true` for `infoblox-ddi`
- Verify `mcp_infoblox.py` exists in project root
- Check `services/infoblox_client.py` exists

### No tools showing up
- Click "System Status" in sidebar to verify servers connected
- Check "Total Tools" count - should show tools from both servers
- Restart the app

## File Structure

```
subnet_mcp/
├── mcp_infoblox.py              # Infoblox MCP server
├── services/
│   └── infoblox_client.py       # Infoblox API client
├── mcp_config.json              # MCP server and agent configs
├── .env                         # Your credentials (gitignored)
├── .env.example                 # Template for credentials
└── INFOBLOX_SETUP.md           # This file
```

## Security Notes

- **Never commit `.env` file** - it contains secrets
- API keys have full access to your Infoblox tenant
- Use read-only keys for testing if available
- Implement approval workflows for production changes
- Monitor API usage in Infoblox portal

## Next Steps

1. **Test with read operations first**: List IP spaces, subnets, DNS records
2. **Test in dev/staging**: Create test subnets and DNS records
3. **Implement workflows**: Combine tools for complete provisioning
4. **Add validation**: Use local subnet calculator before API calls
5. **Create specialized agents**: Add agents for specific tasks

## Support

- Infoblox API Docs: https://csp.infoblox.com/apidoc
- Infoblox Developer Portal: https://www.infoblox.com/developer-portal/
- Project Issues: Check CLAUDE.md for project overview

## Example Session

```
User: "List my IP spaces"
Agent: [Calls list_ip_spaces tool]
Result: Shows all IP spaces with IDs and names

User: "Create a /24 subnet at 10.50.0.0 in the first space"
Agent: [Uses space ID from previous result]
       [Calls create_subnet tool]
Result: Subnet created successfully

User: "Now create DNS zone prod.company.com"
Agent: [Calls create_dns_zone with type=auth]
Result: Zone created

User: "Add A record for web pointing to 10.50.0.10"
Agent: [Uses zone ID from previous result]
       [Calls create_a_record]
Result: DNS record created
```

Enjoy your integrated DDI automation! 🚀
