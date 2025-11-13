"""
Professional Streamlit UI for Multi-Agent System
Modern, polished design with visual hierarchy
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
    initial_sidebar_state="expanded"
)

# Professional CSS with visual appeal
st.markdown("""
<style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    * {
        font-family: 'Inter', sans-serif;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Main container with gradient */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0;
    }

    /* Content wrapper */
    .block-container {
        max-width: 1200px;
        padding: 2rem 1rem;
        background: white;
        border-radius: 20px;
        margin: 2rem auto;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1f36 0%, #0f1419 100%);
        padding: 2rem 1rem;
    }

    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
        font-weight: 700;
    }

    /* Sidebar sections */
    [data-testid="stSidebar"] .element-container {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        backdrop-filter: blur(10px);
    }

    /* Chat messages */
    .stChatMessage {
        background-color: transparent;
        padding: 1.5rem 1rem;
        margin: 0.5rem 0;
    }

    [data-testid="stChatMessageContent"] {
        background: #f8f9fa;
        padding: 1.25rem;
        border-radius: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }

    /* User messages - highlighted */
    .stChatMessage[data-testid*="user"] [data-testid="stChatMessageContent"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }

    .stChatMessage[data-testid*="user"] [data-testid="stChatMessageContent"] * {
        color: white !important;
    }

    /* Assistant messages */
    .stChatMessage[data-testid*="assistant"] [data-testid="stChatMessageContent"] {
        background: #ffffff;
        border: 2px solid #e9ecef;
    }

    /* Chat input */
    .stChatInputContainer {
        border-top: 2px solid #e9ecef;
        padding: 1.5rem 0;
        background: white;
    }

    .stChatInput textarea {
        border-radius: 24px !important;
        border: 2px solid #e9ecef !important;
        padding: 1rem 1.5rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease;
    }

    .stChatInput textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }

    /* Headers */
    h1 {
        font-size: 2rem;
        font-weight: 700;
        color: #1a1f36;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    h2 {
        font-size: 1.25rem;
        font-weight: 600;
        color: #ffffff;
        margin: 1rem 0 0.5rem 0;
    }

    h3 {
        font-size: 1rem;
        font-weight: 600;
        color: #ffffff;
        margin: 0.75rem 0 0.5rem 0;
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.875rem;
        color: rgba(255, 255, 255, 0.7) !important;
        font-weight: 500;
    }

    /* Select boxes */
    .stSelectbox {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 0.5rem;
    }

    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
        color: white !important;
    }

    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }

    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }

    /* Expanders */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border-radius: 12px;
        padding: 1rem;
        font-weight: 600;
        color: #667eea;
        border: 1px solid rgba(102, 126, 234, 0.2);
    }

    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
        border-color: #667eea;
    }

    /* Status badges */
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.5rem 1rem;
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 600;
        color: #10b981;
        margin: 0.5rem 0;
    }

    .status-dot {
        width: 8px;
        height: 8px;
        background: #10b981;
        border-radius: 50%;
        margin-right: 0.5rem;
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    /* Info cards */
    .info-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        backdrop-filter: blur(10px);
    }

    /* Code blocks */
    code {
        background: #f1f3f5;
        color: #667eea;
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
        font-size: 0.9rem;
        font-family: 'Monaco', 'Courier New', monospace;
    }

    pre {
        background: #1a1f36;
        color: #e9ecef;
        padding: 1rem;
        border-radius: 8px;
        overflow-x: auto;
        border: 1px solid #667eea;
    }

    /* Alert boxes */
    .stAlert {
        border-radius: 12px;
        border-left: 4px solid #667eea;
    }

    /* Divider */
    hr {
        margin: 1.5rem 0;
        border: none;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
    }

    ::-webkit-scrollbar-thumb {
        background: rgba(102, 126, 234, 0.5);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: rgba(102, 126, 234, 0.7);
    }
</style>
""", unsafe_allow_html=True)


async def initialize_system():
    """Initialize the orchestrator with MCP servers"""
    orchestrator = get_orchestrator()

    if not orchestrator.is_initialized:
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
    """Render professional sidebar"""
    with st.sidebar:
        st.markdown("# 🤖 Multi-Agent System")
        st.markdown("### Powered by Claude & OpenAI")
        st.markdown("---")

        # Agent selector
        if st.session_state.get("orchestrator_initialized"):
            orchestrator = get_orchestrator()
            available_agents = list(orchestrator.agents.keys())

            st.markdown("### 👤 Active Agent")
            selected_agent = st.selectbox(
                "Select Agent",
                options=available_agents,
                index=0,
                key="selected_agent",
                label_visibility="collapsed"
            )

            agent = orchestrator.agents.get(selected_agent)
            if agent:
                st.markdown(f'<div class="info-card">🧠 <strong>{agent.llm_provider.upper()}</strong><br/>Agent: {selected_agent}</div>', unsafe_allow_html=True)

        st.markdown("---")

        # System status
        st.markdown("### 📊 System Status")

        if st.session_state.get("orchestrator_initialized"):
            orchestrator = get_orchestrator()
            status = orchestrator.get_status()

            st.markdown('<div class="status-badge"><span class="status-dot"></span>Online</div>', unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                st.metric("MCP Servers", len(status["mcp_servers"]))
                st.metric("Agents", len(status["agents"]))
            with col2:
                st.metric("Total Tools", status["total_tools"])
                st.metric("Status", "Ready")

            with st.expander("🔍 View Details", expanded=False):
                st.json(status)
        else:
            st.markdown('<div class="status-badge"><span class="status-dot"></span>Initializing...</div>', unsafe_allow_html=True)

        st.markdown("---")

        # Actions
        st.markdown("### ⚙️ Actions")
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.rerun()


def render_chat():
    """Render chat interface"""

    # Header
    st.markdown("# 💬 Chat with Your Agent")
    st.caption("Ask questions, run commands, and manage your infrastructure")
    st.markdown("---")

    # Get selected agent
    orchestrator = get_orchestrator()
    selected_agent = st.session_state.get("selected_agent")
    if not selected_agent or selected_agent not in orchestrator.agents:
        selected_agent = list(orchestrator.agents.keys())[0]
        st.session_state.selected_agent = selected_agent

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            # Show tool calls
            if "tool_calls" in message and message["tool_calls"]:
                with st.expander(f"🔧 Tool Calls ({len(message['tool_calls'])})"):
                    for i, tool_call in enumerate(message["tool_calls"]):
                        st.markdown(f"**{i+1}. {tool_call['tool']}**")
                        st.code(json.dumps(tool_call["input"], indent=2), language="json")
                        if tool_call.get("result"):
                            st.caption("Result:")
                            result_str = json.dumps(tool_call["result"], indent=2)
                            if len(result_str) > 500:
                                st.code(result_str[:500] + "...", language="json")
                            else:
                                st.code(result_str, language="json")

    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        # Get assistant response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                try:
                    response = asyncio.run(orchestrator.chat(prompt, selected_agent))

                    if response.get("error"):
                        content = f"❌ **Error:** {response['error']}"
                        st.error(content)
                    else:
                        content = response["response"]
                        st.markdown(content)

                        # Show tool calls
                        if response.get("tool_calls"):
                            with st.expander(f"🔧 Tool Calls ({len(response['tool_calls'])})"):
                                for i, tool_call in enumerate(response["tool_calls"]):
                                    st.markdown(f"**{i+1}. {tool_call['tool']}**")
                                    st.code(json.dumps(tool_call["input"], indent=2), language="json")
                                    if tool_call.get("result"):
                                        st.caption("Result:")
                                        result_str = json.dumps(tool_call["result"], indent=2)
                                        if len(result_str) > 500:
                                            st.code(result_str[:500] + "...", language="json")
                                        else:
                                            st.code(result_str, language="json")

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": content,
                        "tool_calls": response.get("tool_calls", [])
                    })

                except Exception as e:
                    content = f"❌ **Error:** {str(e)}"
                    st.error(content)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": content,
                        "tool_calls": []
                    })


async def main_async():
    """Async initialization"""
    try:
        orchestrator = await initialize_system()
        st.session_state["orchestrator_initialized"] = True
        return orchestrator
    except Exception as e:
        st.error(f"❌ Failed to initialize: {str(e)}")
        return None


def main():
    """Main entry point"""

    # Initialize system
    if not st.session_state.get("orchestrator_initialized"):
        with st.spinner("🚀 Initializing Multi-Agent System..."):
            orchestrator = asyncio.run(main_async())
            if orchestrator:
                st.success("✅ System initialized successfully!")
                st.rerun()
    else:
        render_sidebar()
        render_chat()


if __name__ == "__main__":
    main()
