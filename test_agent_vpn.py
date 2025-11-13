#!/usr/bin/env python3
"""
Test VPN creation through agent with natural language
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_vpn_creation():
    """Test VPN creation with the agent using natural language"""

    # Import orchestrator
    from agents.orchestrator import get_orchestrator

    orchestrator = get_orchestrator()

    print("="*70)
    print("TESTING VPN CREATION WITH AGENT")
    print("Testing: 'Create a VPN called Test-VPN-Natural-Language'")
    print("="*70)

    try:
        # Initialize if not already done
        if not orchestrator.initialized:
            print("\n📋 Initializing orchestrator...")
            await orchestrator.initialize(
                mcp_servers=[
                    {
                        "name": "infoblox-ddi",
                        "command": "python3",
                        "args": ["mcp_infoblox.py"],
                        "url": "http://127.0.0.1:3001/sse"
                    }
                ],
                agent_configs=[
                    {
                        "name": "main",
                        "llm_provider": "claude"
                    }
                ]
            )
            print("✅ Orchestrator initialized")

        # Test natural language VPN creation
        print("\n🚀 Sending request to agent...")
        print("Request: 'Create a VPN called Test-VPN-Natural-Language'")

        response = await orchestrator.chat(
            message="Create a VPN called Test-VPN-Natural-Language",
            agent_name="main"
        )

        print("\n📊 AGENT RESPONSE:")
        print("="*70)
        print(response.get("response", "No response"))
        print("="*70)

        if "tool_calls" in response:
            print("\n🔧 TOOL CALLS:")
            for i, tool_call in enumerate(response["tool_calls"], 1):
                print(f"\n  {i}. {tool_call.get('name', 'Unknown tool')}")
                if "input" in tool_call:
                    import json
                    print(f"     Input: {json.dumps(tool_call['input'], indent=6)}")

        # Check if successful
        if "error" in response.get("response", "").lower():
            print("\n❌ VPN Creation Failed")
            return False
        else:
            print("\n✅ VPN Creation Request Processed")
            return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Don't cleanup - server should stay running
        pass

if __name__ == "__main__":
    result = asyncio.run(test_vpn_creation())
    exit(0 if result else 1)
