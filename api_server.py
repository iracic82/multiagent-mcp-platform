"""
FastAPI backend for modern agent UI
"""

import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import json
import os
from agents.orchestrator import get_orchestrator

app = FastAPI(title="AI Agent Platform API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global orchestrator
orchestrator = None


class ChatMessage(BaseModel):
    message: str
    agent_name: str = "main"


class InitRequest(BaseModel):
    llm_provider: Optional[str] = "claude"


@app.on_event("startup")
async def startup_event():
    """Initialize orchestrator on startup"""
    global orchestrator
    orchestrator = get_orchestrator()

    # Initialize with MCP subnet server (SSE)
    await orchestrator.initialize(
        mcp_servers=[
            {
                "name": "subnet",
                "url": "http://localhost:3000/sse"
            }
        ],
        agent_configs=[
            {"name": "main", "llm_provider": os.getenv("DEFAULT_LLM", "claude")}
        ]
    )
    print("✅ Orchestrator initialized with HTTP MCP integration!")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the modern UI"""
    with open("frontend/index.html", "r") as f:
        return f.read()


@app.get("/api/status")
async def get_status():
    """Get system status"""
    if orchestrator and orchestrator.is_initialized:
        return orchestrator.get_status()
    return {"initialized": False}


@app.post("/api/chat")
async def chat(msg: ChatMessage):
    """Chat endpoint"""
    if not orchestrator or not orchestrator.is_initialized:
        return {"error": "System not initialized"}

    try:
        response = await orchestrator.chat(msg.message, msg.agent_name)
        return response
    except Exception as e:
        return {"error": str(e)}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time chat"""
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            msg_data = json.loads(data)

            # Process message
            response = await orchestrator.chat(
                msg_data["message"],
                msg_data.get("agent_name", "main")
            )

            # Send response
            await websocket.send_json(response)

    except WebSocketDisconnect:
        print("Client disconnected")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
