import streamlit as st
from utils.styles import get_css

# Page config
st.set_page_config(
    page_title="About",
    page_icon="ℹ️",
    layout="wide"
)

# Apply shared CSS
st.markdown(f"<style>{get_css()}</style>", unsafe_allow_html=True)

# Title
st.title("ℹ️ About Document Search")

# Main content
st.markdown('<div class="glass-container">', unsafe_allow_html=True)

st.markdown("""
### Overview
This document search application allows you to upload, store, and semantically search through your documents using state-of-the-art AI technology.

### Technology Stack
- **Frontend**: Streamlit
- **Database**: MongoDB Atlas
- **AI/ML**: OpenAI API for embeddings
- **Language**: Python 3.8+
""")

# Architecture Diagram
st.markdown("### System Architecture")

architecture_diagram = """
digraph {
    rankdir=TD;
    node [style=filled, fontcolor=white, fontname="Arial"];
    
    A [label="Web Interface", fillcolor="#4169e1"];
    B [label="Document Processor", fillcolor="#1e90ff"];
    C [label="Text Chunker", fillcolor="#4169e1"];
    D [label="Embeddings", fillcolor="#1e90ff"];
    E [label="MongoDB Atlas", fillcolor="#4169e1"];
    F [label="Search Engine", fillcolor="#1e90ff"];
    
    A -> B [label="Upload"];
    B -> C [label="Extract Text"];
    C -> D [label="Generate"];
    D -> E [label="Store"];
    A -> F [label="Search Query"];
    F -> D [label="Query Embedding"];
    F -> E [label="Vector Search"];
    E -> F [label="Results"];
    F -> A [label="Display"];
}
"""

st.graphviz_chart(architecture_diagram)

# Database Schema
st.markdown("### Database Schema")

schema_diagram = """
digraph {
    rankdir=LR;
    node [shape=record, style=filled, fontcolor=white, fontname="Arial"];
    
    Document [label="{DOCUMENT|string filename\\lstring content\\larray embedding\\larray chunks\\ldate created_at\\l}", fillcolor="#4169e1"];
    Chunk [label="{CHUNK|string text\\larray embedding\\l}", fillcolor="#1e90ff"];
    
    Document -> Chunk [label="contains", dir=both, arrowhead=crow, arrowtail=none];
}
"""

st.graphviz_chart(schema_diagram)

st.markdown("""
### Features
- Document upload and processing
- Semantic search using AI embeddings
- Real-time search results
- Support for multiple file formats
- Dark/Light mode support
- Responsive design
""")

st.markdown('</div>', unsafe_allow_html=True) 