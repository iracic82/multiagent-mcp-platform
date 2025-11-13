"""
Clean, Professional Streamlit UI for Multi-Agent System
Inspired by ChatGPT and Claude interfaces
"""

import asyncio
import streamlit as st
import json
from agents.orchestrator import get_orchestrator

# Page config
st.set_page_config(
    page_title="Multi-Agent System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Clean, professional CSS
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Main container - white background */
    .main {
        background-color: #ffffff;
        padding: 0;
    }

    /* Sidebar - clean dark */
    [data-testid="stSidebar"] {
        background-color: #f7f7f8;
        border-right: 1px solid #e5e5e5;
    }

    /* Chat messages */
    .stChatMessage {
        background-color: transparent;
        border: none;
        padding: 1.5rem 0;
    }

    [data-testid="stChatMessageContent"] {
        padding: 1rem;
        background-color: #f7f7f8;
        border-radius: 1rem;
        max-width: 48rem;
    }

    /* User messages */
    .stChatMessage[data-testid*="user"] [data-testid="stChatMessageContent"] {
        background-color: #f7f7f8;
    }

    /* Assistant messages */
    .stChatMessage[data-testid*="assistant"] [data-testid="stChatMessageContent"] {
        background-color: transparent;
    }

    /* Chat input */
    .stChatInputContainer {
        border-top: 1px solid #e5e5e5;
        padding: 1rem 0;
        max-width: 48rem;
        margin: 0 auto;
    }

    .stChatInput textarea {
        border-radius: 1.5rem;
        border: 1px solid #d1d5db;
        padding: 0.75rem 1rem;
        font-size: 1rem;
    }

    /* Headers */
    h1 {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1f2937;
        margin: 0;
        padding: 1rem 0;
    }

    h2, h3 {
        font-size: 1.125rem;
        font-weight: 600;
        color: #374151;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: transparent;
        border-radius: 0.5rem;
        font-size: 0.875rem;
        color: #6b7280;
        padding: 0.5rem;
    }

    .streamlit-expanderHeader:hover {
        background-color: #f3f4f6;
    }

    /* Tool call styling */
    details {
        border: 1px solid #e5e7eb;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        padding: 0.5rem;
    }

    /* Select box */
    .stSelectbox {
        max-width: 250px;
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem;
        font-weight: 600;
        color: #10b981;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.875rem;
        color: #6b7280;
    }

    /* Buttons */
    .stButton button {
        border-radius: 0.5rem;
        border: 1px solid #d1d5db;
        background-color: white;
        color: #374151;
        font-weight: 500;
        padding: 0.5rem 1rem;
        transition: all 0.2s;
    }

    .stButton button:hover {
        background-color: #f9fafb;
        border-color: #9ca3af;
    }

    /* Status indicator */
    .status-online {
        display: inline-block;
        width: 8px;
        height: 8px;
        background-color: #10b981;
        border-radius: 50%;
        margin-right: 0.5rem;
    }

    /* Container max width */
    .block-container {
        max-width: 56rem;
        padding: 2rem 1rem;
    }

    /* Code blocks */
    code {
        background-color: #f3f4f6;
        color: #1f2937;
        padding: 0.125rem 0.25rem;
        border-radius: 0.25rem;
        font-size: 0.875rem;
    }

    pre {
        background-color: #1f2937;
        color: #f3f4f6;
        padding: 1rem;
        border-radius: 0.5rem;
        overflow-x: auto;
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

        # Get enabled MCP servers
        mcp_servers = []
        for server_name, server_config in config.get("mcpServers", {}).items():
            if server_config.get("enabled", False):
                server_info = {
                    "name": server_name,
                    "command": server_config["command"],
                    "args": server_config["args"]
                }
                if "env" in server_config:
                    server_info["env"] = server_config["env"]
                mcp_servers.append(server_info)

        if not mcp_servers:
            mcp_servers = [{"name": "subnet", "command": "python", "args": ["mcp_server.py"]}]

        # Get enabled agents
        agent_configs = []
        for agent_config in config.get("agentConfigs", []):
            if agent_config.get("enabled", False):
                agent_configs.append({
                    "name": agent_config["name"],
                    "llm_provider": agent_config["llm_provider"],
                    "system_prompt": agent_config.get("system_prompt", "")
                })

        if not agent_configs:
            agent_configs = [{"name": "main", "llm_provider": "claude"}]

        await orchestrator.initialize(
            mcp_servers=mcp_servers,
            agent_configs=agent_configs
        )

    return orchestrator


def render_sidebar():
    """Render clean sidebar"""
    with st.sidebar:
        st.markdown("### Multi-Agent System")
        st.markdown("---")

        # Agent selector
        if st.session_state.get("orchestrator_initialized"):
            orchestrator = get_orchestrator()
            available_agents = list(orchestrator.agents.keys())

            selected_agent = st.selectbox(
                "Active Agent",
                options=available_agents,
                index=0,
                key="selected_agent"
            )

            # Get agent info
            agent = orchestrator.agents.get(selected_agent)
            if agent:
                st.caption(f"Provider: {agent.llm_provider}")

        st.markdown("---")

        # System status
        st.markdown("### System Status")

        if st.session_state.get("orchestrator_initialized"):
            orchestrator = get_orchestrator()
            status = orchestrator.get_status()

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Servers", len(status["mcp_servers"]))
                st.metric("Agents", len(status["agents"]))
            with col2:
                st.metric("Tools", status["total_tools"])
                st.markdown('<span class="status-online"></span>Online', unsafe_allow_html=True)

            with st.expander("Details"):
                st.json(status)
        else:
            st.info("Initializing...")

        st.markdown("---")

        # Clear chat
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()


def render_chat():
    """Render chat interface"""

    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("💬 Chat")

    # Get selected agent
    orchestrator = get_orchestrator()
    selected_agent = st.session_state.get("selected_agent", list(orchestrator.agents.keys())[0])

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            # Show tool calls
            if "tool_calls" in message and message["tool_calls"]:
                with st.expander(f"🔧 Used {len(message['tool_calls'])} tool(s)"):
                    for i, tool_call in enumerate(message["tool_calls"]):
                        st.markdown(f"**{tool_call['tool']}**")
                        st.code(json.dumps(tool_call["input"], indent=2), language="json")
                        if tool_call.get("result"):
                            st.caption("Result:")
                            st.code(json.dumps(tool_call["result"], indent=2)[:500] + "...", language="json")

    # Chat input
    if prompt := st.chat_input("Message..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        # Get assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = asyncio.run(orchestrator.chat(prompt, selected_agent))

                    if response.get("error"):
                        content = f"Error: {response['error']}"
                        st.error(content)
                    else:
                        content = response["response"]
                        st.markdown(content)

                        # Show tool calls
                        if response.get("tool_calls"):
                            with st.expander(f"🔧 Used {len(response['tool_calls'])} tool(s)"):
                                for i, tool_call in enumerate(response["tool_calls"]):
                                    st.markdown(f"**{tool_call['tool']}**")
                                    st.code(json.dumps(tool_call["input"], indent=2), language="json")
                                    if tool_call.get("result"):
                                        st.caption("Result:")
                                        st.code(json.dumps(tool_call["result"], indent=2)[:500] + "...", language="json")

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": content,
                        "tool_calls": response.get("tool_calls", [])
                    })

                except Exception as e:
                    st.error(f"Error: {str(e)}")


async def main_async():
    """Async initialization"""
    try:
        orchestrator = await initialize_system()
        st.session_state["orchestrator_initialized"] = True
        return orchestrator
    except Exception as e:
        st.error(f"Failed to initialize: {str(e)}")
        return None


def main():
    """Main entry point"""

    # Initialize system
    if not st.session_state.get("orchestrator_initialized"):
        with st.spinner("🚀 Starting system..."):
            orchestrator = asyncio.run(main_async())
            if orchestrator:
                st.rerun()
    else:
        render_sidebar()
        render_chat()


if __name__ == "__main__":
    main()
