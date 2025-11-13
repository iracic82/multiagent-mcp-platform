"""
Modern Streamlit UI for Multi-Agent System with MCP Integration
Enhanced with better styling and UX
"""

import asyncio
import streamlit as st
import json
from datetime import datetime
from agents.orchestrator import get_orchestrator


# Page config with modern theme
st.set_page_config(
    page_title="AI Agent Platform",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# Multi-Agent MCP System\nBuilt with Claude & OpenAI"
    }
)

# Modern CSS with dark theme support
st.markdown("""
<style>
    /* Main container */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0;
    }

    /* Chat container */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2d3748 0%, #1a202c 100%);
    }

    [data-testid="stSidebar"] * {
        color: white !important;
    }

    /* Headers */
    h1, h2, h3 {
        color: white;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }

    /* Tool call expander */
    .streamlit-expanderHeader {
        background-color: #f7fafc;
        border-radius: 10px;
        font-weight: 600;
    }

    /* Success/Info boxes */
    .stAlert {
        border-radius: 10px;
        border-left: 5px solid #667eea;
    }

    /* Buttons */
    .stButton>button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }

    /* Chat input */
    .stChatInputContainer {
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 10px;
    }

    /* JSON display */
    code {
        background-color: #2d3748;
        color: #48bb78;
        border-radius: 5px;
        padding: 2px 6px;
    }
</style>
""", unsafe_allow_html=True)


async def initialize_system():
    """Initialize the orchestrator with MCP servers"""
    orchestrator = get_orchestrator()

    if not orchestrator.is_initialized:
        # Load configuration from mcp_config.json
        try:
            with open("mcp_config.json", "r") as f:
                config = json.load(f)
        except FileNotFoundError:
            config = {}

        # Get enabled MCP servers from config
        mcp_servers = []
        for server_name, server_config in config.get("mcpServers", {}).items():
            if server_config.get("enabled", False):
                server_info = {
                    "name": server_name,
                    "command": server_config["command"],
                    "args": server_config["args"]
                }
                # Add environment variables if present
                if "env" in server_config:
                    server_info["env"] = server_config["env"]
                mcp_servers.append(server_info)

        # Fallback if no servers enabled
        if not mcp_servers:
            mcp_servers = [
                {
                    "name": "subnet",
                    "command": "python",
                    "args": ["mcp_server.py"]
                }
            ]

        # Get enabled agent configs from config
        agent_configs = []
        for agent_config in config.get("agentConfigs", []):
            if agent_config.get("enabled", False):
                agent_configs.append({
                    "name": agent_config["name"],
                    "llm_provider": agent_config["llm_provider"],
                    "system_prompt": agent_config.get("system_prompt", "")
                })

        # Fallback if no agents enabled
        if not agent_configs:
            agent_configs = [
                {"name": "main", "llm_provider": st.session_state.get("default_llm", "claude")}
            ]

        await orchestrator.initialize(
            mcp_servers=mcp_servers,
            agent_configs=agent_configs
        )

    return orchestrator


def render_sidebar():
    """Render modern sidebar"""
    with st.sidebar:
        st.markdown("# 🤖 AI Agent Platform")
        st.markdown("---")

        # LLM Selection with icons
        st.markdown("### 🧠 LLM Provider")
        llm_provider = st.selectbox(
            "Choose your brain",
            options=["claude", "openai"],
            index=0 if st.session_state.get("default_llm", "claude") == "claude" else 1,
            key="llm_selector",
            help="Claude: Best for tool use | OpenAI: Alternative LLM"
        )
        st.session_state["default_llm"] = llm_provider

        st.markdown("---")

        # MCP Server Management
        st.markdown("### 📡 MCP Servers")

        with st.expander("➕ Add New Server"):
            with st.form("add_server_form"):
                server_name = st.text_input("Server Name", placeholder="my-mcp-server")
                server_command = st.text_input("Command", value="python")
                server_args = st.text_input("Args", placeholder="server.py, arg1, arg2")

                if st.form_submit_button("Add Server", use_container_width=True):
                    if server_name and server_command:
                        if "mcp_servers" not in st.session_state:
                            st.session_state["mcp_servers"] = []

                        st.session_state["mcp_servers"].append({
                            "name": server_name,
                            "command": server_command,
                            "args": [arg.strip() for arg in server_args.split(",") if arg.strip()]
                        })
                        st.success(f"✅ Added {server_name}!")
                        st.info("🔄 Restart to apply changes")
                    else:
                        st.error("❌ Name and command required")

        # Show configured servers
        if "mcp_servers" in st.session_state:
            st.markdown("**Active Servers:**")
            for i, server in enumerate(st.session_state["mcp_servers"]):
                st.markdown(f"• `{server['name']}`")

        st.markdown("---")

        # System Status
        st.markdown("### 📊 System Status")

        if st.session_state.get("orchestrator_initialized", False):
            orchestrator = get_orchestrator()
            status = orchestrator.get_status()

            col1, col2 = st.columns(2)
            with col1:
                st.metric("🖥️ Servers", len(status["mcp_servers"]))
                st.metric("🤖 Agents", len(status["agents"]))
            with col2:
                st.metric("🔧 Tools", status["total_tools"])
                st.metric("📡 Status", "🟢 Online")

            with st.expander("🔍 Detailed Info"):
                st.json(status)
        else:
            st.info("🔄 Initializing...")

        st.markdown("---")

        # Quick actions
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Reset", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

        with col2:
            if st.button("📋 Clear Chat", use_container_width=True):
                st.session_state.messages = []
                st.rerun()


def format_tool_call(tool_call):
    """Format tool call for display"""
    return f"""
**Tool:** `{tool_call['tool']}`

**Input:**
```json
{json.dumps(tool_call['input'], indent=2)}
```

**Output:**
```json
{json.dumps(tool_call['result'], indent=2)}
```
"""


def render_chat_interface(orchestrator):
    """Render modern chat interface"""
    # Header
    st.markdown("# 💬 Chat with Your Agent")

    # Agent selector
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        available_agents = list(orchestrator.agents.keys())
        if available_agents:
            selected_agent = st.selectbox(
                "Active Agent",
                options=available_agents,
                index=0,
                key="selected_agent",
                help="Select which agent to chat with"
            )
        else:
            st.error("❌ No agents available")
            return

    with col2:
        agent = orchestrator.get_agent(selected_agent)
        if agent:
            st.info(f"🧠 Using: **{agent.llm_provider.upper()}** ({agent.model})")

    with col3:
        message_count = len(st.session_state.get("messages", []))
        st.metric("💬", message_count)

    st.markdown("---")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history with modern styling
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🤖"):
                st.markdown(message["content"])

                # Show tool calls if present
                if "tool_calls" in message and message["tool_calls"]:
                    with st.expander(f"🔧 **{len(message['tool_calls'])} Tool Calls** - Click to expand"):
                        for i, tool_call in enumerate(message["tool_calls"]):
                            st.markdown(f"### Call #{i+1}")
                            st.markdown(format_tool_call(tool_call))
                            st.markdown("---")

    # Chat input
    if prompt := st.chat_input("💭 Ask me anything..."):
        # Display user message
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        st.session_state.messages.append({"role": "user", "content": prompt})

        # Get agent response
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner(f"🤔 {selected_agent} is thinking..."):
                try:
                    response = asyncio.run(orchestrator.chat(prompt, selected_agent))

                    if response.get("error"):
                        st.error(f"❌ **Error:** {response['error']}")
                        content = f"Error: {response['error']}"
                    else:
                        content = response["response"]
                        st.markdown(content)

                        # Show tool calls with modern display
                        if response.get("tool_calls"):
                            with st.expander(f"🔧 **{len(response['tool_calls'])} Tool Calls** - Click to expand"):
                                for i, tool_call in enumerate(response["tool_calls"]):
                                    st.markdown(f"### Call #{i+1}")
                                    st.markdown(format_tool_call(tool_call))
                                    if i < len(response['tool_calls']) - 1:
                                        st.markdown("---")

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": content,
                        "tool_calls": response.get("tool_calls", []),
                        "timestamp": datetime.now().isoformat()
                    })

                except Exception as e:
                    st.error(f"❌ **Error:** {str(e)}")
                    with st.expander("🐛 Debug Info"):
                        st.exception(e)


async def main_async():
    """Async main function"""
    try:
        orchestrator = await initialize_system()
        st.session_state["orchestrator_initialized"] = True
        return orchestrator
    except Exception as e:
        st.error(f"❌ **Initialization Failed:** {str(e)}")
        with st.expander("🐛 Debug Info"):
            st.exception(e)
        return None


def main():
    """Main entry point"""
    render_sidebar()

    # Initialize orchestrator
    if not st.session_state.get("orchestrator_initialized", False):
        with st.spinner("🚀 Initializing AI Agent Platform..."):
            orchestrator = asyncio.run(main_async())
            if orchestrator:
                st.success("✅ System Ready!")
                st.balloons()
                st.rerun()
    else:
        orchestrator = get_orchestrator()
        render_chat_interface(orchestrator)


if __name__ == "__main__":
    main()
