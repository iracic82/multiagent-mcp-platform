# Multi-Agent MCP Platform with Infoblox Integration

**Production-ready Model Context Protocol (MCP) server providing comprehensive integration with Infoblox BloxOne Platform for IPAM, DNS, DHCP, VPN, and Security operations.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-1.0-green.svg)](https://modelcontextprotocol.io)

---

## Overview

This multi-agent platform exposes **48+ enterprise-grade tools** for managing Infoblox BloxOne infrastructure, enabling AI agents to perform network operations through natural language. Built with production features including observability, caching, circuit breakers, and distributed tracing.

### Key Capabilities

- **IPAM Management**: IP spaces, address blocks, subnets, ranges, fixed addresses
- **DNS Operations**: A, AAAA, CNAME, MX, TXT, PTR, SRV records with zone management
- **VPN Provisioning**: End-to-end NIOSXaaS VPN service creation and management
- **Security**: DNS Firewall (Atcfw/DFP) with threat intelligence and content filtering
- **Federation**: Service discovery and configuration across distributed deployments
- **Insights**: Network analytics and utilization reporting
- **Multi-Agent Orchestration**: Multiple specialized agents with task delegation
- **Multi-LLM Support**: Claude and OpenAI integration

### Production Features

**Enterprise Observability**
- Prometheus metrics endpoint (`/metrics`) for monitoring
- Grafana dashboards for visualization
- OpenTelemetry distributed tracing with Jaeger integration
- Structured JSON logging with correlation IDs

**Performance & Reliability**
- Response caching with configurable TTL (3000x speedup for repeated queries)
- Circuit breakers for fast-fail protection against API failures
- Request timeout handling with configurable limits
- Health check endpoints for load balancers and Kubernetes

**Scalability**
- Multi-tenant architecture with concurrent client support
- SSE (Server-Sent Events) transport for real-time communication
- Connection pooling and resource optimization
- Modular service client design for horizontal scaling

**Cloud-Ready Deployment**
- Docker containerization support
- AWS Fargate / ECS deployment ready
- API Gateway / ALB integration
- Auto-scaling based on metrics

---

## Quick Start

### Prerequisites

- Python 3.10+
- Infoblox BloxOne API key ([Get from CSP Portal](https://csp.infoblox.com))
- Optional: Anthropic or OpenAI API key for agent integration

### Installation

```bash
# Clone the repository
git clone https://github.com/iracic82/multiagent-mcp-platform.git
cd multiagent-mcp-platform

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your INFOBLOX_API_KEY
```

### Running the MCP Server

```bash
# Standalone mode (SSE transport on port 3001)
python mcp_infoblox.py
```

The server exposes three endpoints:
- **SSE endpoint**: `http://localhost:3001/sse` (for MCP clients)
- **Metrics endpoint**: `http://localhost:8001/metrics` (for Prometheus)
- **Health endpoint**: `http://localhost:8001/health` (for load balancers)

### Testing the Server

```bash
# Test individual tools
python test_mcp_tools_direct.py

# Test production features
python test_caching.py          # Caching performance
python test_circuit_breaker.py  # Circuit breaker behavior
python test_metrics_server.py   # Metrics collection
python test_tracing.py          # Distributed tracing
```

---

## Available Tools (48+)

<details>
<summary><strong>IPAM Tools (18 tools)</strong></summary>

- `list_ip_spaces` - List all IP spaces
- `get_ip_space` - Get IP space details by ID
- `create_ip_space` - Create new IP space
- `list_address_blocks` - List address blocks
- `create_address_block` - Create address block
- `list_subnets` - List subnets with utilization
- `create_subnet` - Create new subnet
- `get_subnet` - Get subnet details
- `list_fixed_addresses` - List fixed IP assignments
- `create_fixed_address` - Create fixed IP address
- `delete_fixed_address` - Remove fixed IP
- `get_next_available_ip` - Get next free IP from range
- `allocate_next_ip` - Reserve next available IP
- And more...

</details>

<details>
<summary><strong>DNS Data Tools (15 tools)</strong></summary>

- `list_dns_a_records` - List A records
- `create_a_record` - Create A record
- `update_a_record` - Update A record
- `delete_a_record` - Delete A record
- `list_cname_records` - List CNAME records
- `create_cname_record` - Create CNAME
- `list_mx_records` - List MX records
- `create_mx_record` - Create MX record
- `list_txt_records` - List TXT records
- `create_txt_record` - Create TXT record
- `list_ptr_records` - List PTR (reverse DNS)
- And more...

</details>

<details>
<summary><strong>DNS Config Tools (8 tools)</strong></summary>

- `list_auth_zones` - List authoritative zones
- `create_auth_zone` - Create DNS zone
- `get_auth_zone` - Get zone details
- `list_forward_zones` - List forward zones
- `create_forward_zone` - Create forward zone
- `list_dns_views` - List DNS views
- And more...

</details>

<details>
<summary><strong>VPN Tools (5 tools)</strong></summary>

- `list_vpn_services` - List VPN services
- `create_vpn_service` - Create VPN service
- `get_vpn_service` - Get service details
- `create_vpn_access_location` - Create access location
- `update_vpn_access_location` - Update location (tunnel IPs)

</details>

<details>
<summary><strong>Security Tools (Atcfw/DFP)</strong></summary>

- `list_security_policies` - List DNS firewall policies
- `create_security_policy` - Create security policy
- `list_threat_feeds` - List threat intelligence feeds
- And more...

</details>

---

## Architecture

### System Overview

```
┌─────────────────┐
│  MCP Clients    │  (Claude Desktop, Custom Agents, etc.)
│  (SSE)          │
└────────┬────────┘
         │ SSE Transport (Port 3001)
         ▼
┌─────────────────────────────────────────────┐
│         Infoblox MCP Server                 │
│  ┌──────────────────────────────────────┐  │
│  │   FastMCP Framework                   │  │
│  │   - SSE Transport Handler             │  │
│  │   - Tool Registry (48+ tools)         │  │
│  │   - Request/Response Serialization    │  │
│  └──────────────────────────────────────┘  │
│  ┌──────────────────────────────────────┐  │
│  │   Production Middleware               │  │
│  │   - Response Caching (TTL-based)     │  │
│  │   - Circuit Breakers                  │  │
│  │   - Request Timeouts                  │  │
│  │   - Metrics Collection                │  │
│  │   - Distributed Tracing               │  │
│  └──────────────────────────────────────┘  │
│  ┌──────────────────────────────────────┐  │
│  │   Service Clients (Module-level)     │  │
│  │   - InfobloxClient (IPAM/DNS)        │  │
│  │   - NIOSXaaSClient (VPN)             │  │
│  │   - AtcfwClient (Security)           │  │
│  │   - InsightsClient (Analytics)       │  │
│  └──────────────────────────────────────┘  │
└────────┬───────────────────────────────────┘
         │ HTTPS + Bearer Token Auth
         ▼
┌─────────────────────────────────────────────┐
│     Infoblox BloxOne Platform (SaaS)        │
│  - IPAM API (IP spaces, subnets, IPs)      │
│  - DNS Data API (records)                   │
│  - DNS Config API (zones, views)            │
│  - NIOSXaaS API (VPN services)              │
│  - Atcfw/DFP API (security policies)        │
└─────────────────────────────────────────────┘
```

### Multi-Agent Architecture

```
┌──────────────────────────────────────────┐
│         Agent Orchestrator               │
│  - Multi-agent coordination              │
│  - Task delegation                       │
│  - LLM provider abstraction              │
└────────┬─────────────────────────────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌─────────┐ ┌──────────────────┐
│  Main   │ │  Network         │
│  Agent  │ │  Specialist      │
│         │ │  Agent           │
│ (Claude)│ │  (Claude/OpenAI) │
└────┬────┘ └────┬─────────────┘
     │           │
     └─────┬─────┘
           │
           ▼
    ┌──────────────┐
    │  MCP Client  │
    │  (Singleton) │
    └──────┬───────┘
           │
           ▼
    [MCP Servers]
```

### Multi-Tenant Support

The MCP server runs as a **standalone process** and supports multiple concurrent client connections:

- **SSE Transport**: Each client maintains a persistent SSE connection
- **Shared Service Clients**: Module-level singletons for efficient resource usage
- **Per-Connection Context**: Isolated request/response handling
- **Centralized Metrics**: All connections share the same metrics collector

**Deployment Patterns:**
1. **Internal Agent Use**: Single orchestrator with MCP client singleton
2. **External Direct Access**: Multiple clients connecting to SSE endpoint
3. **Hybrid**: Both patterns simultaneously

---

## Observability

### Prometheus Metrics

The server exposes detailed metrics on `http://localhost:8001/metrics`:

**Request Metrics:**
- `mcp_requests_total` - Total API requests by tool, client, status
- `mcp_request_duration_seconds` - Request latency histogram
- `mcp_request_errors_total` - Error count by tool and error type

**Cache Metrics:**
- `cache_hits_total` - Cache hit count by tool
- `cache_misses_total` - Cache miss count
- `cache_hit_rate` - Real-time hit rate percentage
- `cache_size_bytes` - Current cache memory usage
- `cache_entries_total` - Number of cached entries

**Circuit Breaker Metrics:**
- `circuit_breaker_state` - Current state (0=closed, 1=open, 2=half-open)
- `circuit_breaker_failures_total` - Consecutive failure count
- `circuit_breaker_successes_total` - Consecutive success count

**System Metrics:**
- `active_connections` - Current SSE connections
- `uptime_seconds` - Server uptime

### Grafana Dashboards

Pre-configured dashboards available in `docs/grafana/`:
- **MCP Server Overview**: Request rates, latency, error rates
- **Cache Performance**: Hit rates, memory usage, eviction stats
- **Circuit Breaker Status**: State transitions, failure rates
- **Client Analytics**: Per-client request patterns

### Distributed Tracing (Jaeger)

OpenTelemetry integration provides:
- End-to-end request tracing across all API calls
- Automatic HTTP request instrumentation
- Parent-child span relationships
- Error tracking and root cause analysis
- Service dependency mapping

**View traces**: `http://localhost:16686` (Jaeger UI)

---

## Production Deployment

### Docker Deployment

```dockerfile
# Dockerfile included in repository
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 3001 8001
CMD ["python", "mcp_infoblox.py"]
```

```bash
# Build and run
docker build -t infoblox-mcp-server .
docker run -p 3001:3001 -p 8001:8001 \
  -e INFOBLOX_API_KEY=your_key \
  -e INFOBLOX_BASE_URL=https://csp.infoblox.com \
  infoblox-mcp-server
```

### AWS Fargate Deployment

**Architecture:**
```
Internet → ALB → Fargate (MCP Server) → Infoblox API
              ↓
         CloudWatch Logs
              ↓
         Prometheus/Grafana
```

**Key Components:**
- **Application Load Balancer**: SSL termination, health checks
- **AWS Fargate**: Serverless container hosting with auto-scaling
- **CloudWatch**: Log aggregation and monitoring
- **Prometheus**: Metrics scraping from `/metrics` endpoint
- **Jaeger**: Distributed tracing collection

**Benefits:**
- Auto-scaling based on CPU/memory or custom metrics
- Zero server management
- Multi-AZ high availability
- Pay-per-use pricing
- Health check integration (`/health` endpoint)

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for complete deployment instructions.

---

## Configuration

### Environment Variables

```bash
# Infoblox API
INFOBLOX_API_KEY=your_api_key_here
INFOBLOX_BASE_URL=https://csp.infoblox.com

# Performance
CACHE_ENABLED=true
CACHE_TTL=300                    # 5 minutes default
REQUEST_TIMEOUT=30               # seconds

# Circuit Breaker
CIRCUIT_BREAKER_ENABLED=true
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
CIRCUIT_BREAKER_TIMEOUT=60       # seconds

# Observability
TRACING_ENABLED=true
JAEGER_HOST=localhost
JAEGER_PORT=6831
METRICS_PORT=8001

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json                  # or 'console'
```

### Performance Tuning

**Cache Configuration:**
- Adjust `CACHE_TTL` based on data change frequency
- Monitor `cache_hit_rate` metric
- Default 300s works well for IPAM data

**Circuit Breaker:**
- `FAILURE_THRESHOLD=5`: Number of failures before opening circuit
- `TIMEOUT=60`: Seconds to wait before retry (half-open state)
- Monitor `circuit_breaker_state` metric

**Request Timeouts:**
- Default 30s covers most operations
- Increase for large list operations
- Decrease for real-time requirements

---

## Project Structure

```
multiagent-mcp-platform/
├── agents/                     # Agent framework
│   ├── base_agent.py          # Multi-LLM agent implementation
│   ├── mcp_client.py          # MCP client (SSE transport)
│   └── orchestrator.py        # Multi-agent orchestration
├── services/                   # Business logic and clients
│   ├── infoblox_client.py     # Infoblox IPAM/DNS client
│   ├── niosxaas_client.py     # NIOSXaaS VPN client
│   ├── atcfw_client.py        # Atcfw/DFP security client
│   ├── insights_client.py     # Analytics client
│   ├── metrics.py             # Metrics collection
│   ├── metrics_server.py      # Prometheus endpoint
│   └── tracing.py             # OpenTelemetry tracing
├── mcp_infoblox.py            # Main MCP server (48+ tools)
├── mcp_config.json            # MCP server and agent configuration
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Container definition
├── ARCHITECTURE.md            # System architecture documentation
├── DEPLOYMENT_GUIDE.md        # Production deployment guide
└── IMPROVEMENTS_CHANGELOG.md  # Feature implementation log
```

---

## Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)**: Complete system architecture and design patterns
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)**: Production deployment strategies (Docker, Fargate, K8s)
- **[IMPROVEMENTS_CHANGELOG.md](IMPROVEMENTS_CHANGELOG.md)**: Production feature implementation log
- **[CLAUDE.md](CLAUDE.md)**: Developer guidance and project conventions

---

## Testing

```bash
# Run all tests
python -m pytest

# Test specific features
python test_caching.py              # Cache performance (3000x speedup demo)
python test_circuit_breaker.py      # Circuit breaker behavior
python test_metrics_server.py       # Prometheus metrics
python test_tracing.py              # Distributed tracing

# Integration tests
python test_mcp_tools_direct.py     # Direct tool invocation
python test_vpn_update.py           # End-to-end VPN workflow
```

---

## Contributing

Contributions welcome! This platform is designed as a **template** for building production-grade MCP servers for any REST API.

**Reusable Patterns:**
- Multi-agent orchestration
- Caching layer (adapt for any API)
- Circuit breaker implementation
- Metrics collection framework
- Distributed tracing integration
- Health check endpoints
- Docker/Fargate deployment configs

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

MIT License - See [LICENSE](LICENSE) file for details.

---

## Acknowledgments

Built with:
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP server framework
- [Infoblox BloxOne Platform](https://www.infoblox.com/products/bloxone-ddi/) - API integration
- [OpenTelemetry](https://opentelemetry.io/) - Distributed tracing
- [Prometheus](https://prometheus.io/) - Metrics collection
- [Structlog](https://www.structlog.org/) - Structured logging

---

## Support

- **Issues**: [GitHub Issues](https://github.com/iracic82/multiagent-mcp-platform/issues)
- **Documentation**: See `docs/` directory
- **Infoblox API**: [BloxOne API Documentation](https://csp.infoblox.com/apidoc)

---

**Status**: Production-Ready | Enterprise-Grade | Observable | High-Performance
