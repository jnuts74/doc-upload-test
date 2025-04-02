import streamlit as st
from utils.styles import get_css, apply_custom_styles
from utils.sqlite_client import SQLiteClient
from utils.mongodb import mongodb
from utils.logger import logger

# Page config
st.set_page_config(
    page_title="Settings",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply custom styles
apply_custom_styles()

# Top Navigation
st.markdown("""
<style>
    .top-nav {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 2rem;
        padding: 1rem;
        background-color: #1E1E1E;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .nav-item {
        color: #FFFFFF;
        text-decoration: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        transition: background-color 0.3s;
        font-weight: 500;
        cursor: pointer;
    }
    
    .nav-item:hover {
        background-color: #333333;
    }
    
    .nav-item.active {
        background-color: #4169e1;
    }
</style>
""", unsafe_allow_html=True)

# Navigation
nav_items = {
    "🏠 Home": "Home",
    "🔍 Search": "pages/1_Document_Search",
    "📚 Library": "pages/2_Document_Library",
    "⚙️ Settings": "",
    "📋 Logs": "pages/4_Logs"
}

# Create navigation container
nav_container = st.container()
nav_cols = nav_container.columns(len(nav_items))

# Add navigation items
for idx, (label, page) in enumerate(nav_items.items()):
    with nav_cols[idx]:
        if st.button(
            label,
            key=f"nav_{page}",
            use_container_width=True,
            type="secondary" if page else "primary"
        ):
            if page:
                st.switch_page(page + ".py")

# Apply shared CSS
st.markdown(f"<style>{get_css()}</style>", unsafe_allow_html=True)

# Initialize SQLite client
sqlite_client = SQLiteClient()

# Title
st.title("⚙️ Settings")

# Get current credentials
current_credentials = sqlite_client.get_credentials() or {}

# API Configuration section
st.markdown("### 🔑 API Configuration")

# OpenAI API Key
openai_key = st.text_input(
    "OpenAI API Key",
    value=current_credentials.get('openai_api_key', ''),
    type="password",
    help="Your OpenAI API key for embeddings generation"
)

# MongoDB Connection String
mongodb_uri = st.text_input(
    "MongoDB Connection String",
    value=current_credentials.get('mongodb_uri', ''),
    type="password",
    help="Your MongoDB connection string for document storage"
)

# Save button
if st.button("💾 Save Settings", type="primary"):
    try:
        # Save to SQLite
        if sqlite_client.save_credentials(mongodb_uri, openai_key):
            # Update session state
            st.session_state['mongodb_uri'] = mongodb_uri
            st.session_state['openai_api_key'] = openai_key
            
            # Try to connect to MongoDB with new credentials
            try:
                mongodb.connect()
                st.success("✅ Settings saved successfully! MongoDB connection tested and working.")
            except Exception as e:
                st.error(f"Settings saved but MongoDB connection failed: {str(e)}")
        else:
            st.error("Failed to save settings.")
            
    except Exception as e:
        st.error(f"Error saving settings: {str(e)}")

# Clear settings button
if st.button("🗑️ Clear Settings", type="secondary"):
    try:
        if sqlite_client.clear_credentials():
            # Clear session state
            st.session_state.pop('mongodb_uri', None)
            st.session_state.pop('openai_api_key', None)
            # Close MongoDB connection
            mongodb.close()
            st.success("Settings cleared successfully!")
            st.experimental_rerun()
        else:
            st.error("Failed to clear settings.")
    except Exception as e:
        st.error(f"Error clearing settings: {str(e)}")

# Connection Status
st.markdown("### 📡 Connection Status")

# Check MongoDB connection
mongodb_status = "🟢 Connected" if mongodb.is_connected() else "🔴 Disconnected"
st.markdown(f"**MongoDB Status:** {mongodb_status}")

# OpenAI API Status (we could add a test call here if needed)
openai_status = "🟢 Configured" if st.session_state.get('openai_api_key') else "🔴 Not Configured"
st.markdown(f"**OpenAI API Status:** {openai_status}")

# Add some helpful information
st.markdown("### ℹ️ Information")
st.markdown("""
- The OpenAI API key is used for generating embeddings for semantic search
- MongoDB is used for storing documents and their embeddings
- Both credentials are required for the application to function properly
- Credentials are stored securely in a local SQLite database
""")

# Footer with version info
st.markdown("---")
st.markdown("**Version:** 1.0.0 | **Build:** 2024.03.14") 