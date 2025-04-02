import streamlit as st
from utils.mongodb import MongoDB
from utils.openai_client import OpenAIClient
from utils.styles import get_css, apply_custom_styles
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="Search Documents",
    page_icon="🔍",
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
    "🔍 Search": "",
    "📚 Library": "pages/2_Document_Library",
    "⚙️ Settings": "pages/5_Settings",
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

# Custom CSS for search page
st.markdown("""
<style>
/* Search button styling */
.stButton>button {
    background: linear-gradient(to right, #1e3c72, #2a5298);
    color: white;
    border: none;
    padding: 0.5rem 2rem;
    border-radius: 5px;
    font-weight: bold;
    transition: all 0.3s ease;
}

.stButton>button:hover {
    background: linear-gradient(to right, #2a5298, #1e3c72);
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

/* Slider styling */
.stSlider>div>div>div {
    background: linear-gradient(to right, #1e3c72, #2a5298);
}

/* Result card styling */
.result-card {
    background: #1E1E1E;
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    border: 1px solid #333;
    color: #FFFFFF;
}

.result-card:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    transform: translateX(4px);
    transition: all 0.3s ease;
    border-color: #4169e1;
}

.result-card h4 {
    color: #FFFFFF;
    margin-bottom: 1rem;
    font-size: 1.1rem;
}

/* Relevance score styling */
.relevance-score {
    color: #4169e1;
    font-weight: bold;
    font-size: 0.9rem;
    margin-bottom: 1rem;
    display: inline-block;
    padding: 0.3rem 0.8rem;
    background: rgba(65, 105, 225, 0.1);
    border-radius: 4px;
}

/* View document link styling */
.view-doc {
    color: #4169e1;
    text-decoration: none;
    font-weight: 500;
    display: inline-block;
    margin-top: 1rem;
    padding: 0.5rem 1rem;
    background: rgba(65, 105, 225, 0.1);
    border-radius: 4px;
    transition: all 0.2s ease;
}

.view-doc:hover {
    background: rgba(65, 105, 225, 0.2);
    transform: translateX(2px);
}

/* Search result text */
.result-text {
    color: #CCC;
    font-size: 0.95rem;
    line-height: 1.5;
    margin: 1rem 0;
    padding: 1rem;
    background: rgba(0,0,0,0.2);
    border-radius: 4px;
    border-left: 3px solid #4169e1;
}
</style>
""", unsafe_allow_html=True)

# Main title
st.title("🔍 Document Search")

# Check for API credentials
if not st.session_state.get('mongodb_uri') or not st.session_state.get('openai_api_key'):
    st.warning("⚠️ Please configure your API credentials in the Settings page before searching.")
    st.markdown("[Go to Settings ➜](Settings)")
    st.stop()

# Search interface
search_col1, search_col2 = st.columns([3, 1])

with search_col1:
    search_query = st.text_input("Enter your search query:", placeholder="What would you like to find?")

with search_col2:
    num_results = st.slider("Number of results:", min_value=1, max_value=10, value=5)

# Search button
if st.button("🔍 Search", type="primary"):
    if not search_query:
        st.error("Please enter a search query.")
    else:
        try:
            with st.spinner("Searching documents..."):
                # Get embedding for search query
                openai_client = OpenAIClient()
                query_embedding = openai_client.get_embedding(search_query)
                
                # Search documents
                mongodb = MongoDB()
                results = mongodb.search_documents(query_embedding, limit=num_results)
                
                if not results:
                    st.info("No matching documents found.")
                else:
                    st.markdown(f"### Found {len(results)} matching documents")
                    
                    # Display results
                    for result in results:
                        # Calculate relevance percentage
                        relevance = int(result['similarity'] * 100)
                        
                        # Create unique button key for this result
                        view_key = f"view_{result['filename'].replace('.', '_')}"
                        
                        st.markdown(f"""
                        <div class="result-card">
                            <h4>📄 {result['filename']}</h4>
                            <div class="relevance-score">🎯 Relevance: {relevance}%</div>
                            <div class="result-text">{result['best_chunk']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Add view button with proper session state handling
                        if st.button("👁️ View Full Document", key=view_key):
                            st.session_state.viewing_document = result['filename']
                            st.switch_page("pages/2_Document_Library.py")
        except Exception as e:
            st.error(f"Error performing search: {str(e)}")
            if "API key" in str(e):
                st.markdown("Please check your API credentials in the [Settings](Settings) page.")
            elif "MongoDB" in str(e):
                st.markdown("Please check your MongoDB connection string in the [Settings](Settings) page.") 