# MCP HTTP Migration Guide

## ✅ MIGRATION COMPLETE - November 18, 2025

**Status**: Successfully migrated all 4 MCP servers from deprecated SSE transport to spec-compliant HTTP streamable transport.

## Overview

This guide documents the **completed migration** from deprecated SSE transport to spec-compliant HTTP streamable transport for all MCP servers in the multi-agent platform.

## Background

As of January 2025, the Model Context Protocol (MCP) specification has deprecated Server-Sent Events (SSE) transport in favor of HTTP streamable transport. This migration ensures our platform remains compliant with the official MCP spec.

**Migration Results:**
- ✅ **HTTP Transport**: Successfully deployed and operational (spec-compliant)
- ✅ **SSE Transport**: Still available as backup on ports 3001-3004
- ✅ **Client Implementation**: Fixed and using `streamablehttp_client` from MCP SDK
- 📚 **Reference**: https://modelcontextprotocol.io/docs/concepts/transports

## Migration Strategy: Parallel Deployment with Fallback

We implemented a **zero-downtime migration** strategy:

1. **Both transports run simultaneously** on different ports
2. **Client attempts HTTP first**, falls back to SSE if HTTP unavailable
3. **No service interruption** during transition
4. **Gradual migration** once HTTP is proven stable

### Port Mapping

| Service | SSE (Backup) | HTTP (New) | Tools |
|---------|--------------|------------|-------|
| Infoblox DDI | 3001/sse | 4001/mcp | 98 |
| Subnet Calculator | 3002/sse | 4002/mcp | 2 |
| AWS Tools | 3003/sse | 4003/mcp | 27 |
| AWS CloudControl | 3004/sse | 4004/mcp | 6 |

## Files Created

### HTTP MCP Servers

All HTTP servers are **identical** to SSE versions except for the transport configuration:

1. **mcp_server_http.py** (Subnet Calculator)
   - Port: 4002
   - Endpoint: http://127.0.0.1:4002/mcp
   - Tools: calculate_subnet_info, validate_cidr

2. **mcp_infoblox_http.py** (Infoblox BloxOne DDI)
   - Port: 4001
   - Endpoint: http://127.0.0.1:4001/mcp
   - Tools: 98 tools across IPAM, DNS, DHCP, VPN, Security, SOC Insights

3. **mcp_aws_http.py** (AWS Tools)
   - Port: 4003
   - Endpoint: http://127.0.0.1:4003/mcp
   - Tools: 27 tools for VPC, VGW, VPN, Subnets, Security Groups

4. **mcp_aws_cloudcontrol_http.py** (AWS CloudControl)
   - Port: 4004
   - Endpoint: http://127.0.0.1:4004/mcp
   - Tools: 6 tools for universal AWS resource management

### Key Code Changes

Each HTTP server has this transport configuration:

```python
if __name__ == "__main__":
    mcp.run(
        transport="http",      # ✅ Spec-compliant
        host="127.0.0.1",
        port=4001,             # New port range 4001-4004
        path="/mcp"            # HTTP endpoint path
    )
```

Compare to deprecated SSE version:

```python
if __name__ == "__main__":
    mcp.run(transport="sse", port=3001)  # ⚠️ Deprecated
```

### Client Fallback Logic

**agents/mcp_client.py** now implements HTTP-first with SSE fallback:

```python
async def connect_server(self, server_name: str, url: str):
    """
    Connect with HTTP-first, SSE-fallback strategy.

    URLs are automatically converted:
    - http://host:port/sse -> tries http://host:port/mcp, falls back to /sse
    - http://host:port/mcp -> uses HTTP, falls back to SSE
    """
    # Try HTTP first (spec-compliant)
    try:
        await self._connect_http(server_name, http_url)
        logger.info(f"✅ Connected via HTTP")
        return
    except Exception as http_error:
        logger.warning(f"HTTP failed, falling back to SSE")

    # Fallback to SSE (deprecated)
    try:
        await self._connect_sse(server_name, sse_url)
        logger.info(f"⚠️  Connected via SSE (fallback)")
    except Exception as sse_error:
        raise Exception("Both transports failed")
```

### Startup Script

**start_http_servers.sh** - Launches all HTTP servers in parallel:

```bash
./start_http_servers.sh
```

Features:
- ✅ Starts all 4 HTTP servers in background
- ✅ Health checks all endpoints
- ✅ Logs to `logs/*_http.log`
- ✅ Clean shutdown with Ctrl+C
- ✅ Monitors server health every 30 seconds

## Testing the Migration

### 1. Verify Current SSE Servers Running

Your current SSE servers should already be running on ports 3001-3004. Check:

```bash
lsof -i :3001  # Infoblox SSE
lsof -i :3002  # Subnet SSE
lsof -i :3003  # AWS Tools SSE
lsof -i :3004  # CloudControl SSE
```

### 2. Start HTTP Servers

Launch all HTTP servers:

```bash
cd /Users/iracic/PycharmProjects/subnet_mcp
./start_http_servers.sh
```

Expected output:
```
✅ Infoblox DDI HTTP Server (port 4001)
✅ Subnet Calculator HTTP Server (port 4002)
✅ AWS Tools HTTP Server (port 4003)
✅ AWS CloudControl HTTP Server (port 4004)
```

### 3. Verify HTTP Endpoints

Test each HTTP endpoint:

```bash
curl http://127.0.0.1:4001/mcp
curl http://127.0.0.1:4002/mcp
curl http://127.0.0.1:4003/mcp
curl http://127.0.0.1:4004/mcp
```

### 4. Test Client Fallback

The mcp_client.py will now:
1. Try HTTP endpoints first (4001-4004/mcp)
2. Fall back to SSE if HTTP fails (3001-3004/sse)

You can verify this by checking logs when the system starts.

### 5. Monitor Logs

Check HTTP server logs:

```bash
tail -f logs/infoblox_http.log
tail -f logs/subnet_http.log
tail -f logs/aws_http.log
tail -f logs/cloudcontrol_http.log
```

## Migration Path Forward

### Phase 1: Parallel Operation (Current)
- ✅ Both SSE and HTTP servers running
- ✅ Client tries HTTP first, falls back to SSE
- ✅ Zero downtime, full backward compatibility
- **Duration**: 1-2 weeks of testing

### Phase 2: HTTP Primary (Future)
- Monitor HTTP server stability
- Ensure all tool calls work correctly
- Verify no performance degradation
- **Duration**: 2-4 weeks

### Phase 3: SSE Deprecation (Final)
- Stop SSE servers (ports 3001-3004)
- Remove SSE fallback from client
- Remove old SSE server files
- Update documentation

## Rollback Procedure

If issues occur with HTTP servers:

1. **Stop HTTP servers**:
   ```bash
   # Get PIDs from start_http_servers.sh output, then:
   kill <INFOBLOX_PID> <SUBNET_PID> <AWS_PID> <CLOUDCONTROL_PID>
   ```

2. **System automatically falls back to SSE** (ports 3001-3004)

3. **No code changes needed** - fallback is automatic

## Important Notes

### HTTP Client Implementation ✅ COMPLETE

The `_connect_http()` method in `agents/mcp_client.py` now uses the **official MCP SDK HTTP client**.

**Implementation Details:**

The key fix was properly unpacking the `streamablehttp_client` response tuple:

```python
from mcp.client.streamable_http import streamablehttp_client

async def _connect_http(self, server_name: str, url: str):
    """Connect to MCP server via HTTP transport (spec-compliant streamable HTTP)"""
    exit_stack = AsyncExitStack()
    self.exit_stacks[server_name] = exit_stack

    try:
        # streamablehttp_client returns (read_stream, write_stream, get_session_id)
        streams = await exit_stack.enter_async_context(
            streamablehttp_client(
                url=url,
                timeout=30.0,  # Explicit float for HTTP operations
                sse_read_timeout=300.0  # Explicit float for SSE read operations
            )
        )

        # ⚡ CRITICAL FIX: Unpack tuple - ClientSession only needs first 2 items
        read_stream, write_stream, get_session_id = streams

        # Create session with read and write streams only
        session = await exit_stack.enter_async_context(
            ClientSession(read_stream, write_stream)
        )

        await session.initialize()

        # Store session and session ID callback
        self.sessions[server_name] = session
        self.servers[server_name] = {
            "url": url,
            "transport": "http",
            "get_session_id": get_session_id
        }

        # Get available tools
        response = await session.list_tools()
        # ... tool registration

        logger.info(f"✅ HTTP connection established to {server_name}")
```

**The Bug We Fixed:**

Initially, we were passing all 3 tuple items to `ClientSession(*streams)`, which expected only 2 (read_stream, write_stream). This caused runtime errors:
- `'function' object has no attribute 'total_seconds'`
- `RuntimeError: Attempted to exit cancel scope in a different task`

**The Solution:**

Properly unpack the tuple and pass only the streams to ClientSession:
```python
read_stream, write_stream, get_session_id = streams
session = ClientSession(read_stream, write_stream)  # Only 2 args
```

**Verified Working:**
- All 4 MCP servers successfully connected via HTTP
- Protocol version 2025-06-18 negotiated
- Session IDs received for all connections
- 133 tools available across all servers

### Transport Selection

FastMCP supports 3 transports:

1. **stdio** - For local/desktop applications (Claude Desktop)
2. **http** - For web deployments (✅ **spec-compliant**)
3. **sse** - Legacy compatibility (⚠️ **deprecated**)

Reference: https://github.com/jlowin/fastmcp

### What Changed vs What Stayed Same

**Changed:**
- Transport method (SSE → HTTP)
- Server ports (3001-3004 → 4001-4004)
- Endpoint paths (/sse → /mcp)

**Identical:**
- All tool definitions
- Tool functionality
- Input/output schemas
- Service layer code
- Business logic

## Troubleshooting

### HTTP Server Won't Start

**Symptom**: Port already in use

**Solution**:
```bash
# Find process using the port
lsof -i :4001

# Kill it
kill -9 <PID>

# Restart
./start_http_servers.sh
```

### Client Can't Connect

**Symptom**: Both HTTP and SSE fail

**Check**:
1. Are SSE servers running? (ports 3001-3004)
2. Are HTTP servers running? (ports 4001-4004)
3. Check logs for error messages
4. Verify network connectivity

**Solution**:
```bash
# Restart SSE servers (existing process)
# Restart HTTP servers
./start_http_servers.sh
```

### Tools Not Showing Up

**Symptom**: Connected but no tools available

**Cause**: Tool discovery happens during connection initialization

**Solution**:
- Check server logs for initialization errors
- Verify Infoblox API key is set: `echo $INFOBLOX_API_KEY`
- Verify AWS credentials are configured

## Summary

✅ **Migration COMPLETE** (November 18, 2025):
- 4 HTTP MCP servers created and running (ports 4001-4004)
- HTTP client successfully implemented using official MCP SDK
- All connections using HTTP streamable transport (spec-compliant)
- Zero downtime deployment achieved
- 133 tools available via HTTP transport

✅ **Current State** (Phase 2 - HTTP Primary):
- **Primary**: HTTP servers on ports 4001-4004 (active, spec-compliant)
- **Backup**: SSE servers on ports 3001-3004 (available for fallback)
- **Client**: Using `streamablehttp_client` from MCP SDK
- **Protocol**: MCP 2025-06-18
- **Status**: Production-ready ✅

🎯 **Verified Working**:
```
✅ Connected to subnet-calculator via HTTP (spec-compliant) - 2 tools
✅ Connected to infoblox-ddi via HTTP (spec-compliant) - 98 tools
✅ Connected to aws-tools via HTTP (spec-compliant) - 27 tools
✅ Connected to aws-cloudcontrol via HTTP (spec-compliant) - 6 tools
```

🚀 **Next Steps**:
1. ✅ ~~Test HTTP servers~~ - DONE
2. Monitor HTTP stability for 1-2 weeks
3. ✅ ~~Update HTTP client~~ - DONE (using streamablehttp_client)
4. Optional: Deprecate SSE servers after validation period
5. Optional: Remove SSE fallback code

## Questions?

- **SSE deprecation**: https://modelcontextprotocol.io/docs/concepts/transports#server-sent-events-sse-deprecated
- **FastMCP docs**: https://github.com/jlowin/fastmcp
- **MCP specification**: https://modelcontextprotocol.io/

---

**Migration Date**: November 18, 2025
**Status**: ✅ COMPLETE - Phase 2 (HTTP Primary)
**Transport**: HTTP Streamable (MCP Protocol 2025-06-18)
**Backward Compatible**: ✅ Yes (SSE fallback available)
**Production Ready**: ✅ Yes
**Tools Available**: 133 tools across 4 MCP servers
