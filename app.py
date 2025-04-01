import streamlit as st
from utils.mongodb import mongodb
from utils.openai_client import openai_client
from utils.styles import get_css
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="Document Search",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply shared CSS
st.markdown(f"<style>{get_css()}</style>", unsafe_allow_html=True)

# Main title
st.title("🔍 Document Search")

# Search interface
st.markdown('<div class="search-container glass-container">', unsafe_allow_html=True)

# Search input
search_query = st.text_input("", placeholder="Type your search query here...")

# Search button
if st.button("Search Documents", type="primary"):
    if search_query:
        try:
            # Get embedding for search query
            query_embedding = openai_client.get_embedding(search_query)
            
            # Search in MongoDB
            results = mongodb.search_documents(query_embedding)
            
            if results:
                st.markdown("### Search Results")
                for result in results:
                    st.markdown(f"""
                        <div class="card">
                            <h4>📄 {result['filename']}</h4>
                            <p>{result['chunks'][0]['text'][:200]}...</p>
                            <div class="metadata">
                                🕒 Uploaded: {result['created_at'].strftime('%Y-%m-%d %H:%M')}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No matching documents found. Try a different search query.")
        except Exception as e:
            st.error(f"Error performing search: {str(e)}")
    else:
        st.warning("Please enter a search query to begin.")

st.markdown('</div>', unsafe_allow_html=True) 