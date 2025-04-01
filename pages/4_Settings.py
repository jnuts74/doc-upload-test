import streamlit as st
from utils.styles import get_css
from utils.credentials_manager import credentials_manager

# Page config
st.set_page_config(
    page_title="Settings",
    page_icon="⚙️",
    layout="wide"
)

# Apply shared CSS
st.markdown(f"<style>{get_css()}</style>", unsafe_allow_html=True)

# Title
st.title("⚙️ Settings")

# Initialize session state for API keys if not exists
if 'openai_api_key' not in st.session_state:
    saved_openai_key = credentials_manager.get_credential('openai_api_key')
    st.session_state.openai_api_key = saved_openai_key or ""
    
if 'mongodb_uri' not in st.session_state:
    saved_mongodb_uri = credentials_manager.get_credential('mongodb_uri')
    st.session_state.mongodb_uri = saved_mongodb_uri or ""

# Main content
st.markdown("""
### API Configuration
Configure your API keys and connection strings for the application. Your credentials will be stored securely on your local machine.
""")

# OpenAI API Key
with st.expander("OpenAI API Settings", expanded=True):
    st.markdown("""
    The OpenAI API key is required for generating document embeddings and semantic search functionality.
    You can get your API key from the [OpenAI dashboard](https://platform.openai.com/api-keys).
    """)
    
    openai_key = st.text_input(
        "OpenAI API Key",
        value=st.session_state.openai_api_key,
        type="password",
        help="Enter your OpenAI API key"
    )
    
    if openai_key:
        st.session_state.openai_api_key = openai_key
        if len(openai_key) < 20:  # Basic validation
            st.warning("This doesn't look like a valid OpenAI API key. Please check and try again.")

# MongoDB Connection
with st.expander("MongoDB Connection Settings", expanded=True):
    st.markdown("""
    The MongoDB connection string is required for storing and retrieving documents and their embeddings.
    You can get your connection string from [MongoDB Atlas](https://www.mongodb.com/atlas/database).
    """)
    
    mongodb_uri = st.text_input(
        "MongoDB Connection String",
        value=st.session_state.mongodb_uri,
        type="password",
        help="Enter your MongoDB connection string"
    )
    
    if mongodb_uri:
        st.session_state.mongodb_uri = mongodb_uri
        if not mongodb_uri.startswith("mongodb+srv://"):
            st.warning("This doesn't look like a valid MongoDB Atlas connection string. Please check and try again.")

# Save Settings
st.markdown("### Save or Clear Settings")
save_col, clear_col, _ = st.columns([1.2, 1.2, 2.6])

with save_col:
    if st.button("💾 Save Settings", key="save_settings", use_container_width=True):
        if openai_key and mongodb_uri:
            # Save to local encrypted storage
            credentials_manager.save_credential('openai_api_key', openai_key)
            credentials_manager.save_credential('mongodb_uri', mongodb_uri)
            
            st.success("✅ Settings saved successfully!")
        else:
            st.error("Please provide both credentials.")

with clear_col:
    if st.button("🗑️ Clear Saved Settings", key="clear_settings", use_container_width=True):
        credentials_manager.clear_all()
        st.session_state.openai_api_key = ""
        st.session_state.mongodb_uri = ""
        st.success("✅ Credentials cleared!") 