"""
FastAPI backend for Next.js frontend
Provides WebSocket and REST API for multi-agent system
"""

import asyncio
import json
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from agents.orchestrator import get_orchestrator

app = FastAPI(title="Velocity Agent API")

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global orchestrator
orchestrator = None


class ChatMessage(BaseModel):
    message: str
    agent: str = "main"


@app.on_event("startup")
async def startup_event():
    """Initialize orchestrator on startup"""
    global orchestrator
    orchestrator = get_orchestrator()

    # Load MCP config
    import json
    with open("mcp_config.json", "r") as f:
        config = json.load(f)

    # Extract MCP servers and agent configs
    mcp_servers = []
    for name, server_config in config.get("mcpServers", {}).items():
        if server_config.get("enabled", True):
            # Build URL from command and args
            if "url" in server_config:
                mcp_servers.append({"name": name, "url": server_config["url"]})
            else:
                # Try HTTP first (spec-compliant), fallback to SSE (deprecated)
                # HTTP servers on ports 4001-4004/mcp (new)
                # SSE servers on ports 3001-3004/sse (backup)
                port_map = {
                    "subnet-calculator": 4002,
                    "infoblox-ddi": 4001,
                    "aws-tools": 4003,
                    "aws-cloudcontrol": 4004
                }
                port = port_map.get(name, 4000)
                # FastMCP HTTP servers use /mcp endpoint
                mcp_servers.append({"name": name, "url": f"http://127.0.0.1:{port}/mcp"})

    agent_configs = config.get("agentConfigs", [])
    enabled_agents = [a for a in agent_configs if a.get("enabled", True)]

    # Initialize orchestrator
    await orchestrator.initialize(
        mcp_servers=mcp_servers,
        agent_configs=enabled_agents
    )
    print(f"✅ Orchestrator initialized with {len(orchestrator.agents)} agents")
    print(f"✅ Connected to {len(orchestrator.mcp_client.servers)} MCP servers")


@app.get("/api/status")
async def get_status():
    """Get system status"""
    if orchestrator and orchestrator.is_initialized:
        status = orchestrator.get_status()
        return JSONResponse(content=status)
    return JSONResponse(content={"initialized": False, "error": "System not initialized"})


@app.get("/api/agents")
async def get_agents():
    """Get list of available agents"""
    if orchestrator and orchestrator.is_initialized:
        agents = []
        for agent_name, agent in orchestrator.agents.items():
            agents.append({
                "name": agent_name,
                "llm_provider": agent.llm_provider,
                "enabled": True
            })
        return JSONResponse(content={"agents": agents})
    return JSONResponse(content={"agents": []})


@app.get("/api/registry")
async def get_registry():
    """Agent registry for A2A (Agent-to-Agent) communication"""
    if not orchestrator or not orchestrator.is_initialized:
        return JSONResponse(content={
            "agents": [],
            "total_tools": 0,
            "version": "1.0.0",
            "protocol": "A2A-REST",
            "error": "System not initialized"
        })

    # Build agent list with capabilities
    agents = []
    for agent_name, agent in orchestrator.agents.items():
        # Get MCP server capabilities
        capabilities = []
        for server_name, tools in orchestrator.mcp_client.available_tools.items():
            tool_count = len(tools)
            capabilities.append(f"{server_name}: {tool_count} tools")

        agents.append({
            "name": agent_name,
            "llm_provider": agent.llm_provider,
            "endpoint": "http://localhost:8000/api/chat",
            "description": agent.system_prompt.split('\n')[0] if hasattr(agent, 'system_prompt') else f"{agent_name.replace('_', ' ').title()} agent",
            "capabilities": capabilities
        })

    # Get MCP server info
    mcp_servers = {}
    total_tools = 0
    for server_name, tools in orchestrator.mcp_client.available_tools.items():
        tool_count = len(tools)
        total_tools += tool_count
        server_info = orchestrator.mcp_client.servers.get(server_name, {})
        mcp_servers[server_name] = {
            "tools": tool_count,
            "url": server_info.get("url", "unknown")
        }

    return JSONResponse(content={
        "agents": agents,
        "total_tools": total_tools,
        "mcp_servers": mcp_servers,
        "version": "1.0.0",
        "protocol": "A2A-REST"
    })


@app.post("/api/chat")
async def chat(msg: ChatMessage):
    """REST chat endpoint"""
    if not orchestrator or not orchestrator.is_initialized:
        return JSONResponse(content={"success": False, "error": "System not initialized"}, status_code=503)

    try:
        response = await orchestrator.chat(msg.message, msg.agent)
        # Add success field for A2A compatibility
        response["success"] = response.get("error") is None
        return JSONResponse(content=response)
    except Exception as e:
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time chat"""
    await websocket.accept()
    print("✅ WebSocket client connected")

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            msg_data = json.loads(data)

            message = msg_data.get("message", "")
            agent_name = msg_data.get("agent", "main")

            if not message:
                await websocket.send_json({
                    "type": "error",
                    "content": "Empty message"
                })
                continue

            # Send thinking status
            await websocket.send_json({
                "type": "status",
                "status": "thinking"
            })

            try:
                # Process message with agent
                response = await orchestrator.chat(message, agent_name)

                # Send response
                await websocket.send_json({
                    "type": "response",
                    "content": response.get("response", ""),
                    "tool_calls": response.get("tool_calls", []),
                    "agent": agent_name
                })

            except Exception as e:
                print(f"❌ Error processing message: {e}")
                await websocket.send_json({
                    "type": "error",
                    "content": f"Error: {str(e)}"
                })

    except WebSocketDisconnect:
        print("🔌 WebSocket client disconnected")
    except Exception as e:
        print(f"❌ WebSocket error: {e}")


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """File upload endpoint"""
    try:
        contents = await file.read()
        return JSONResponse(content={
            "filename": file.filename,
            "size": len(contents),
            "content_type": file.content_type
        })
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
