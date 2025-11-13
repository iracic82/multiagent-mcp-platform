"""
Test script for the agent system
"""

import asyncio
import os
from dotenv import load_dotenv
from agents.orchestrator import get_orchestrator


async def test_basic_agent():
    """Test basic agent functionality"""
    print("\n" + "="*60)
    print("TEST 1: Basic Agent Functionality")
    print("="*60)

    load_dotenv()

    # Check for API keys
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  ANTHROPIC_API_KEY not set in .env file")
        print("   Create .env file from .env.example and add your API key")
        return False

    orchestrator = get_orchestrator()

    # Initialize with subnet MCP server
    mcp_servers = [
        {
            "name": "subnet",
            "command": "python",
            "args": ["mcp_server.py"]
        }
    ]

    agent_configs = [
        {"name": "main", "llm_provider": "claude"}
    ]

    try:
        await orchestrator.initialize(
            mcp_servers=mcp_servers,
            agent_configs=agent_configs
        )

        # Test 1: Simple subnet calculation
        print("\n📝 Test: Calculate subnet for 192.168.1.0/24")
        response = await orchestrator.chat(
            "What is the subnet information for 192.168.1.0/24? Please use the calculate tool.",
            agent_name="main"
        )

        print(f"\n🤖 Agent Response:")
        print(response["response"])

        if response.get("tool_calls"):
            print(f"\n🔧 Tools Used: {len(response['tool_calls'])}")
            for tool_call in response["tool_calls"]:
                print(f"   - {tool_call['tool']}")

        print("\n✅ Test 1 PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Test 1 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        await orchestrator.cleanup()


async def test_multi_llm():
    """Test multiple LLM providers"""
    print("\n" + "="*60)
    print("TEST 2: Multiple LLM Providers")
    print("="*60)

    load_dotenv()

    # Check for API keys
    has_claude = bool(os.getenv("ANTHROPIC_API_KEY"))
    has_openai = bool(os.getenv("OPENAI_API_KEY"))

    if not has_claude and not has_openai:
        print("⚠️  No API keys found. Skipping test.")
        return False

    orchestrator = get_orchestrator()

    agent_configs = []
    if has_claude:
        agent_configs.append({"name": "claude_agent", "llm_provider": "claude"})
    if has_openai:
        agent_configs.append({"name": "openai_agent", "llm_provider": "openai"})

    try:
        await orchestrator.initialize(
            mcp_servers=[{"name": "subnet", "command": "python", "args": ["mcp_server.py"]}],
            agent_configs=agent_configs
        )

        # Test each agent
        for agent_name in orchestrator.agents.keys():
            print(f"\n📝 Testing {agent_name}...")
            response = await orchestrator.chat(
                "Calculate subnet info for 10.0.0.0/16",
                agent_name=agent_name
            )
            print(f"   Response received: {len(response['response'])} chars")
            print(f"   Tools used: {len(response.get('tool_calls', []))}")

        print("\n✅ Test 2 PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Test 2 FAILED: {e}")
        return False

    finally:
        await orchestrator.cleanup()


async def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 AGENT SYSTEM TESTS")
    print("="*60)

    results = []

    # Test 1: Basic functionality
    result = await test_basic_agent()
    results.append(("Basic Agent", result))

    # Test 2: Multi-LLM
    result = await test_multi_llm()
    results.append(("Multi-LLM", result))

    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)

    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")

    total_passed = sum(1 for _, passed in results if passed)
    print(f"\nTotal: {total_passed}/{len(results)} tests passed")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
