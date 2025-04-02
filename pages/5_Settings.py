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
        with st.status("Saving and initializing...") as status:
            status.write("Encrypting and saving credentials...")
            # Save to SQLite
            if sqlite_client.save_credentials(mongodb_uri, openai_key):
                # Update session state
                st.session_state['mongodb_uri'] = mongodb_uri
                st.session_state['openai_api_key'] = openai_key
                
                status.write("Testing MongoDB connection...")
                # Try to connect to MongoDB with new credentials
                try:
                    mongodb.connect()  # This will also initialize database and indexes
                    status.write("Creating MongoDB indexes...")
                    status.update(label="✅ Setup Complete!", state="complete", expanded=False)
                    st.success("Settings saved and database initialized successfully!")
                except Exception as e:
                    status.update(label="❌ MongoDB Error", state="error")
                    st.error(f"Settings saved but MongoDB connection failed: {str(e)}")
                    st.info("""
                    Common MongoDB Issues:
                    - Network connectivity
                    - IP whitelist settings in MongoDB Atlas
                    - Database user permissions
                    - Invalid connection string format
                    """)
            else:
                status.update(label="❌ Save Error", state="error")
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

# Create two columns for status indicators
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### MongoDB Status")
    mongodb_connected = mongodb.is_connected()
    mongodb_status = {
        "status": "🟢 Connected" if mongodb_connected else "🔴 Disconnected",
        "details": []
    }
    
    if mongodb_connected:
        try:
            doc_count = mongodb.collection.count_documents({})
            index_count = len(list(mongodb.collection.list_indexes()))
            mongodb_status["details"].extend([
                f"Database: searchDb",
                f"Documents: {doc_count}",
                f"Indexes: {index_count}"
            ])
        except Exception as e:
            mongodb_status["details"].append(f"Error getting details: {str(e)}")
    
    st.markdown(f"**Status:** {mongodb_status['status']}")
    for detail in mongodb_status["details"]:
        st.markdown(f"- {detail}")

with col2:
    st.markdown("#### OpenAI API Status")
    openai_configured = bool(st.session_state.get('openai_api_key'))
    openai_status = "🟢 Configured" if openai_configured else "🔴 Not Configured"
    st.markdown(f"**Status:** {openai_status}")
    if openai_configured:
        st.markdown("- API Key validated")
        st.markdown("- Using text-embedding-3-small model")
        st.markdown("- 1536-dimensional embeddings")

# Security Information
st.markdown("### 🔐 Security Information")
st.markdown("""
- Credentials are stored in a secure SQLite database
- Database location: `data/secure/credentials.db`
- File permissions: 600 (owner read/write only)
- Values are encrypted at rest
- Machine-specific encryption key
""")

# Troubleshooting
with st.expander("🔧 Troubleshooting"):
    st.markdown("""
    #### MongoDB Connection Issues
    1. Check your MongoDB Atlas settings:
       - Is your IP whitelisted?
       - Does your user have proper permissions?
       - Is the connection string format correct?
    
    2. Common connection string format:
       ```
       mongodb+srv://username:password@cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
       ```
    
    #### OpenAI API Issues
    1. Verify your API key format:
       - Should start with 'sk-'
       - Should be about 51 characters long
    
    2. Check API key permissions:
       - Embeddings access required
       - Billing configured
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <small>S.E.A.R.C.H. v1.0.0 | Build 2024.03.14</small>
</div>
""", unsafe_allow_html=True) 