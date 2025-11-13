"""
Base agent with Claude and OpenAI support, MCP tool integration
"""

import asyncio
import json
from typing import Any, Dict, List, Optional, Literal
from anthropic import Anthropic
from openai import OpenAI
from agents.mcp_client import get_mcp_client


class BaseAgent:
    """
    General-purpose agent with:
    - Claude or OpenAI as LLM
    - Multi-MCP server tool calling
    - Agent-to-agent communication
    """

    def __init__(
        self,
        name: str,
        llm_provider: Literal["claude", "openai"] = "claude",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096
    ):
        """
        Initialize the agent.

        Args:
            name: Agent identifier
            llm_provider: "claude" or "openai"
            api_key: API key for the LLM provider
            model: Model name (defaults to latest)
            system_prompt: System prompt for the agent
            max_tokens: Maximum tokens for responses
        """
        self.name = name
        self.llm_provider = llm_provider
        self.max_tokens = max_tokens

        # Initialize LLM client
        if llm_provider == "claude":
            self.client = Anthropic(api_key=api_key)
            self.model = model or "claude-3-5-sonnet-20241022"
        elif llm_provider == "openai":
            self.client = OpenAI(api_key=api_key)
            self.model = model or "gpt-4-turbo-preview"
        else:
            raise ValueError(f"Unknown LLM provider: {llm_provider}")

        self.system_prompt = system_prompt or self._default_system_prompt()
        self.conversation_history: List[Dict[str, Any]] = []
        self.mcp_client = get_mcp_client()
        self.agent_registry: Dict[str, 'BaseAgent'] = {}

    def _default_system_prompt(self) -> str:
        return f"""You are {self.name}, a general-purpose AI agent with access to multiple tools and MCP servers.

You can:
1. Call tools from connected MCP servers (subnet calculator, AWS, Terraform, etc.)
2. Delegate tasks to other specialized agents
3. Combine multiple tools to solve complex problems

When using tools:
- Choose the most appropriate tool for the task
- Tools are prefixed with their server name (e.g., "subnet__calculate_subnet_info")
- Parse results carefully and provide clear explanations

Be helpful, accurate, and efficient."""

    def register_agent(self, agent_name: str, agent: 'BaseAgent'):
        """Register another agent for delegation"""
        self.agent_registry[agent_name] = agent

    def _get_agent_delegation_tool(self) -> Dict[str, Any]:
        """Create a tool definition for agent delegation"""
        if not self.agent_registry:
            return None

        return {
            "name": "delegate_to_agent",
            "description": "Delegate a task to another specialized agent. Use this when another agent has better expertise for the task.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "agent_name": {
                        "type": "string",
                        "description": f"Name of the agent to delegate to",
                        "enum": list(self.agent_registry.keys())
                    },
                    "task": {
                        "type": "string",
                        "description": "The task or question to send to the agent"
                    }
                },
                "required": ["agent_name", "task"]
            }
        }

    async def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool (MCP or internal)"""
        # Check if it's agent delegation
        if tool_name == "delegate_to_agent":
            agent_name = tool_input["agent_name"]
            task = tool_input["task"]

            if agent_name not in self.agent_registry:
                return {"error": f"Agent not found: {agent_name}"}

            target_agent = self.agent_registry[agent_name]
            result = await target_agent.chat(task)
            return {
                "agent": agent_name,
                "response": result["response"],
                "delegated": True
            }

        # Otherwise, it's an MCP tool
        try:
            server_name, actual_tool_name = self.mcp_client.parse_tool_call(tool_name)
            result = await self.mcp_client.call_tool(server_name, actual_tool_name, tool_input)
            return result
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}

    async def chat(self, user_message: str) -> Dict[str, Any]:
        """
        Process a user message and return response.

        Args:
            user_message: The user's message

        Returns:
            Dictionary with response, tool calls, and metadata
        """
        response_data = {
            "agent": self.name,
            "llm_provider": self.llm_provider,
            "response": "",
            "tool_calls": [],
            "error": None
        }

        try:
            if self.llm_provider == "claude":
                return await self._chat_claude(user_message, response_data)
            else:
                return await self._chat_openai(user_message, response_data)
        except Exception as e:
            response_data["error"] = str(e)
            response_data["response"] = f"Error: {str(e)}"
            return response_data

    async def _chat_claude(self, user_message: str, response_data: Dict) -> Dict[str, Any]:
        """Handle conversation with Claude"""
        # Add user message
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Get available tools
        mcp_tools = self.mcp_client.get_tools_for_llm()
        agent_tool = self._get_agent_delegation_tool()
        tools = mcp_tools + ([agent_tool] if agent_tool else [])

        # Add cache_control to tools for prompt caching (massive cost savings!)
        if tools:
            # Mark the last tool with cache_control for tool caching
            tools[-1]["cache_control"] = {"type": "ephemeral"}

        # Agentic loop
        while True:
            # Prepare system prompt with cache control for prompt caching
            system_blocks = [
                {
                    "type": "text",
                    "text": self.system_prompt,
                    "cache_control": {"type": "ephemeral"}
                }
            ]

            # Add cache control to conversation history (cache older messages)
            messages = self.conversation_history.copy()
            if len(messages) > 3:
                # Cache everything except the last few messages
                messages[-4]["cache_control"] = {"type": "ephemeral"}

            # Only pass tools if we have some (Claude rejects empty list)
            api_params = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "system": system_blocks,
                "messages": messages
            }
            if tools:
                api_params["tools"] = tools

            response = self.client.messages.create(**api_params)

            if response.stop_reason == "end_turn":
                # Extract final response
                for block in response.content:
                    if block.type == "text":
                        response_data["response"] = block.text
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response.content
                })
                break

            elif response.stop_reason == "tool_use":
                # Process tool calls
                assistant_content = []
                tool_results = []

                for block in response.content:
                    assistant_content.append(block)

                    if block.type == "tool_use":
                        tool_name = block.name
                        tool_input = block.input

                        # Execute tool
                        tool_result = await self._execute_tool(tool_name, tool_input)

                        response_data["tool_calls"].append({
                            "tool": tool_name,
                            "input": tool_input,
                            "result": tool_result
                        })

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(tool_result)
                        })

                # Update conversation history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": assistant_content
                })
                self.conversation_history.append({
                    "role": "user",
                    "content": tool_results
                })
            else:
                response_data["response"] = f"Unexpected stop: {response.stop_reason}"
                break

        return response_data

    async def _chat_openai(self, user_message: str, response_data: Dict) -> Dict[str, Any]:
        """Handle conversation with OpenAI"""
        # Convert history to OpenAI format
        messages = [{"role": "system", "content": self.system_prompt}]

        for msg in self.conversation_history:
            if msg["role"] in ["user", "assistant"]:
                messages.append({
                    "role": msg["role"],
                    "content": str(msg.get("content", ""))
                })

        messages.append({"role": "user", "content": user_message})

        # Get tools
        mcp_tools = self.mcp_client.get_tools_for_llm()
        agent_tool = self._get_agent_delegation_tool()
        tools = mcp_tools + ([agent_tool] if agent_tool else [])

        # Convert tools to OpenAI format
        openai_tools = [
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["input_schema"]
                }
            }
            for tool in tools
        ] if tools else None

        # Agentic loop
        while True:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=openai_tools,
                max_tokens=self.max_tokens
            )

            message = response.choices[0].message

            if message.tool_calls:
                # Process tool calls
                messages.append(message)

                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_input = json.loads(tool_call.function.arguments)

                    # Execute tool
                    tool_result = await self._execute_tool(tool_name, tool_input)

                    response_data["tool_calls"].append({
                        "tool": tool_name,
                        "input": tool_input,
                        "result": tool_result
                    })

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(tool_result)
                    })
            else:
                # Final response
                response_data["response"] = message.content
                self.conversation_history.append({"role": "user", "content": user_message})
                self.conversation_history.append({"role": "assistant", "content": message.content})
                break

        return response_data

    def reset_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []

    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics"""
        return {
            "name": self.name,
            "llm_provider": self.llm_provider,
            "model": self.model,
            "conversation_length": len(self.conversation_history),
            "registered_agents": list(self.agent_registry.keys()),
            "available_mcp_servers": list(self.mcp_client.servers.keys()),
            "total_tools": len(self.mcp_client.get_all_tools())
        }
