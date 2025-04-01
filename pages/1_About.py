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

st.markdown("""
A modern web application for document upload, vectorization, and semantic search using OpenAI embeddings and MongoDB Atlas.

## 🚀 Features

- Document upload and processing
- Text chunking and vectorization using OpenAI's text-embedding-3-small model
- Vector storage in MongoDB Atlas
- Semantic search capabilities
- Dark mode support
- Responsive design
- Document library with card-based interface
- Interactive document preview
- Secure local credential management

## 🛠️ Technology Stack

### Frontend
- **Streamlit**: Modern web application framework for Python
- **Custom CSS**: Styled components and responsive design

### Backend
- **Python 3.12**: Core programming language
- **OpenAI API**: Text embedding generation using `text-embedding-3-small` model
- **MongoDB Atlas**: Vector database for document storage and retrieval
- **LangChain**: Text processing and chunking utilities
- **SQLite**: Local encrypted credential storage
- **Cryptography**: Secure credential encryption

### Key Libraries
- `openai==1.12.0`: OpenAI API client
- `pymongo==4.6.2`: MongoDB driver
- `langchain==0.1.12`: Text processing utilities
- `cryptography==42.0.5`: Credential encryption
- `httpx==0.24.1`: Modern HTTP client
""")

# Architecture Diagram
st.markdown("## 🏗️ System Architecture")

architecture_diagram = """
digraph {
    rankdir=TD;
    node [style=filled, fontcolor=white, fontname="Arial"];
    
    A [label="User Interface/Streamlit", fillcolor="#ff69b4"];
    B [label="Document Upload", fillcolor="#4169e1"];
    C [label="Text Processing/LangChain", fillcolor="#4169e1"];
    D [label="OpenAI Embeddings", fillcolor="#4169e1"];
    E [label="MongoDB Atlas", fillcolor="#228b22"];
    F [label="Search Interface", fillcolor="#ff69b4"];
    G [label="Settings Interface", fillcolor="#ff69b4"];
    H [label="Credential Manager", fillcolor="#daa520"];
    I [label="Local SQLite DB", shape=cylinder, fillcolor="#4b0082"];
    
    A -> B [label="Upload"];
    B -> C [label="Process"];
    C -> D [label="Generate"];
    D -> E [label="Store"];
    A -> F [label="Search"];
    F -> E [label="Query"];
    A -> G [label="Configure"];
    G -> H [label="Manage"];
    H -> I [label="Store/Load"];
    H -> D [label="Provide Key"];
    H -> E [label="Provide URI"];
}
"""

st.graphviz_chart(architecture_diagram)

st.markdown("""
### Process Flow
1. **Credential Management**
   - User enters API credentials in Settings
   - Credentials encrypted using machine-specific key
   - Stored in local SQLite database
   - Loaded into session state when needed

2. **Document Upload**
   - User uploads document through Streamlit interface
   - File is read and converted to text

3. **Text Processing**
   - Document is split into chunks using LangChain
   - Chunk size: 1000 characters
   - Overlap: 200 characters
   - Ensures context preservation

4. **Embedding Generation**
   - Each chunk is sent to OpenAI API
   - Using `text-embedding-3-small` model
   - Generates 1536-dimensional vectors

5. **Storage**
   - Vectors stored in MongoDB Atlas
   - Document metadata preserved
   - Timestamps added for tracking

6. **Search Process**
   - User enters search query
   - Query converted to embedding
   - Vector similarity search performed
   - Results ranked by relevance

## 📊 Database Schemas
""")

# Database Schema Diagram
schema_diagram = """
digraph {
    rankdir=LR;
    node [shape=record, style=filled, fontcolor=white, fontname="Arial"];
    
    Document [label="{Document|filename: String\\lcontent: String\\lembedding: Array\\lchunks: Array\\lcreated_at: DateTime\\l}", fillcolor="#4169e1"];
    Chunk [label="{Chunk|text: String\\lembedding: Array\\l}", fillcolor="#1e90ff"];
    Credentials [label="{Credentials|key: String\\lvalue: String\\lcreated_at: DateTime\\l}", fillcolor="#4b0082"];
    
    Document -> Chunk [label="contains", dir=both, arrowhead=crow, arrowtail=none];
}
"""

st.graphviz_chart(schema_diagram)

st.markdown("""
### Indexes
- MongoDB: `created_at`: 1 (for sorting by upload date)
- MongoDB: `chunks.embedding`: "vectorSearch" (for vector similarity search)

## 🔐 Credential Management

The application uses a secure local credential management system:

1. **Storage Location**: `~/.docsearch/credentials.db` (SQLite database)
2. **Encryption**: 
   - Machine-specific encryption key
   - Generated using PBKDF2 with SHA256
   - Stored in `~/.docsearch/.key`
3. **Credentials Stored**:
   - OpenAI API Key
   - MongoDB Connection String
4. **Security Features**:
   - Encrypted at rest
   - Never exposed in environment variables
   - Session-based access
   - Can be cleared via Settings page

## 🔮 Future Enhancements

1. **Search Improvements**
   - Implement vector similarity search
   - Add relevance scoring
   - Support for multiple document types

2. **User Experience**
   - Document preview
   - Search history
   - Batch processing

3. **Performance**
   - Caching layer
   - Async processing
   - Rate limiting

4. **Security**
   - User authentication
   - Document encryption
   - Access control
   - Enhanced credential encryption
""") 