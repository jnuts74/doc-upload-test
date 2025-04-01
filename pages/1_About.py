import streamlit as st
import graphviz

st.set_page_config(
    page_title="About - Document Search & Upload",
    page_icon="ℹ️",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    /* Main content area */
    .main {
        background-color: var(--background-color);
    }
    
    /* Content containers */
    .stMarkdown {
        background-color: var(--input-background-color);
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        color: var(--text-color);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: var(--primary-color) !important;
    }
    
    /* Code blocks */
    pre {
        background-color: var(--code-background-color) !important;
        color: var(--code-text-color) !important;
    }
    
    /* Links */
    a {
        color: var(--primary-color) !important;
    }
    
    /* Lists */
    ul, ol {
        color: var(--text-color) !important;
    }
    
    /* Graphviz container */
    .graphviz {
        background-color: var(--input-background-color);
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 20px 0;
    }
    </style>
""", unsafe_allow_html=True)

st.title("ℹ️ About This Application")

# Technology Stack
st.header("Technology Stack")
st.markdown("""
### Frontend
- **Streamlit**: Modern web application framework for Python
- **Custom CSS**: Styled components and responsive design

### Backend
- **Python 3.12**: Core programming language
- **OpenAI API**: Text embedding generation using `text-embedding-3-small` model
- **MongoDB Atlas**: Vector database for document storage and retrieval
- **LangChain**: Text processing and chunking utilities

### Key Libraries
- `openai==1.12.0`: OpenAI API client
- `pymongo==4.6.2`: MongoDB driver
- `langchain==0.1.12`: Text processing utilities
- `python-dotenv==1.0.1`: Environment variable management
- `httpx==0.24.1`: Modern HTTP client
""")

# Architecture Diagram
st.header("System Architecture")
st.markdown('<div class="graphviz">', unsafe_allow_html=True)
dot = graphviz.Digraph(comment='System Architecture')
dot.attr(rankdir='TB')

# Add nodes
dot.node('A', 'User Interface\n(Streamlit)')
dot.node('B', 'Document Upload')
dot.node('C', 'Text Processing\n(LangChain)')
dot.node('D', 'OpenAI Embeddings')
dot.node('E', 'MongoDB Atlas\n(Vector Store)')
dot.node('F', 'Search Interface')

# Add edges
dot.edge('A', 'B', 'Upload')
dot.edge('B', 'C', 'Process')
dot.edge('C', 'D', 'Generate')
dot.edge('D', 'E', 'Store')
dot.edge('A', 'F', 'Query')
dot.edge('F', 'E', 'Search')

st.graphviz_chart(dot)
st.markdown('</div>', unsafe_allow_html=True)

# Process Flow
st.header("Process Flow")
st.markdown("""
1. **Document Upload**
   - User uploads document through Streamlit interface
   - File is read and converted to text

2. **Text Processing**
   - Document is split into chunks using LangChain
   - Chunk size: 1000 characters
   - Overlap: 200 characters
   - Ensures context preservation

3. **Embedding Generation**
   - Each chunk is sent to OpenAI API
   - Using `text-embedding-3-small` model
   - Generates 1536-dimensional vectors

4. **Storage**
   - Vectors stored in MongoDB Atlas
   - Document metadata preserved
   - Timestamps added for tracking

5. **Search Process**
   - User enters search query
   - Query converted to embedding
   - Vector similarity search performed
   - Results ranked by relevance
""")

# Database Schema
st.header("Database Schema")
st.markdown("""
### MongoDB Collection: `documents`

```json
{
    "_id": ObjectId,
    "filename": String,
    "created_at": DateTime,
    "chunks": [
        {
            "text": String,
            "embedding": [Float]  // 1536-dimensional vector
        }
    ]
}
```

### Indexes
- `created_at`: 1 (for sorting by upload date)
- `chunks.embedding`: "vectorSearch" (for vector similarity search)
""")

# Future Enhancements
st.header("Future Enhancements")
st.markdown("""
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
""") 