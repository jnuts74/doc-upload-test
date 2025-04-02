import streamlit as st
from utils.styles import get_css, apply_custom_styles
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Document Search AI",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply custom styles
apply_custom_styles()

# Apply shared CSS
st.markdown(f"<style>{get_css()}</style>", unsafe_allow_html=True)

# Custom CSS for top navigation and centered layout
st.markdown("""
<style>
    /* Hide sidebar */
    [data-testid="stSidebar"] {
        display: none;
    }
    
    /* Top Navigation Bar */
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
    
    /* Center all content */
    .main .block-container {
        max-width: 1200px;
        padding-top: 1rem;
        padding-right: 1rem;
        padding-left: 1rem;
        padding-bottom: 1rem;
        margin: 0 auto;
    }
    
    /* Enhance hero section */
    .hero-container {
        text-align: center;
        margin-bottom: 3rem;
    }
    
    .hero-subtitle {
        font-size: 1.2rem;
        color: #666;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Navigation
nav_items = {
    "🏠 Home": "",
    "🔍 Search": "pages/1_Document_Search",
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

# Hero section
st.markdown("""
<div class="hero-container">
    <h1>🔍 Document Search AI</h1>
    <p class="hero-subtitle">Intelligent Document Processing & Semantic Search</p>
</div>
""", unsafe_allow_html=True)

# Quick Start Guide section
st.markdown("### 🚀 Quick Start Guide")
step1, step2, step3, step4, step5, step6 = st.columns(6)

with step1:
    st.markdown("""
    #### 1. Setup
    [Settings ➜](Settings)
    - Get OpenAI key
    - Configure MongoDB
    - Enter credentials
    """)

with step2:
    st.markdown("""
    #### 2. Upload
    [Library ➜](Document_Library)
    - PDF & TXT files
    - Batch upload
    - Auto-processing
    """)

with step3:
    st.markdown("""
    #### 3. Process
    [Library ➜](Document_Library)
    - Text extraction
    - Smart chunking
    - Vector embedding
    """)

with step4:
    st.markdown("""
    #### 4. Search
    [Search ➜](Document_Search)
    - Enter query
    - Semantic matching
    - Context-aware
    """)

with step5:
    st.markdown("""
    #### 5. Review
    [Search ➜](Document_Search)
    - Ranked results
    - Quick preview
    - Full document
    """)

with step6:
    st.markdown("""
    #### 6. Manage
    [Settings ➜](Settings)
    - Monitor status
    - Update settings
    - Secure storage
    """)

# Features section
st.markdown("### ✨ Features & Workflow")

# Create 2x2 grid for features
row1_col1, row1_col2 = st.columns(2)
row2_col1, row2_col2 = st.columns(2)

with row1_col1:
    with st.expander("📥 Document Processing"):
        st.markdown("""
        1. Upload PDF/TXT
        2. Text extraction
        3. Smart chunking
        4. Vector embedding
        5. Secure storage
        """)

with row1_col2:
    with st.expander("🔍 Search Capabilities"):
        st.markdown("""
        1. Semantic search
        2. Relevance ranking
        3. Context preservation
        4. Quick previews
        5. Full document access
        """)

with row2_col1:
    with st.expander("🔐 Security Features"):
        st.markdown("""
        1. Encrypted credentials
        2. Secure document storage
        3. Local processing
        4. Access controls
        5. Data isolation
        """)

with row2_col2:
    with st.expander("🔧 Technical Details"):
        st.markdown("""
        **Core Components**
        - Streamlit UI Framework
        - OpenAI Embeddings API
        - MongoDB Vector Search
        - Python 3.12+ Backend
        
        **Key Libraries**
        - `openai==1.12.0`
        - `pymongo==4.6.2`
        - `streamlit==1.32.0`
        - `PyPDF2==3.0.1`
        """)

# System Architecture and Database Schema section
st.markdown("### 🏗️ System Design")
arch_left, arch_right = st.columns([1, 1])

with arch_left:
    st.markdown("#### Application Architecture")
    st.markdown("""
    <div style="text-align: right; color: #666; margin-bottom: 10px;">Click diagram to enlarge</div>
    """, unsafe_allow_html=True)
    
    st.graphviz_chart("""
    digraph {
        bgcolor="#0E1117";
        rankdir=TB;
        graph [size="5.5,5.5"];
        node [style=filled, fontcolor=white, fontname="Arial", shape=box, fontsize=11, margin=0.2, width=2, height=0.5];
        edge [color="#4169e1", penwidth=1, arrowsize=0.8];
        
        # UI Layer
        UI [label="User Interface/Streamlit", fillcolor="#ff69b4"];
        
        # Second Layer
        DocUpload [label="Document Upload", fillcolor="#4169e1"];
        Settings [label="Settings Interface", fillcolor="#ff69b4"];
        
        # Processing Layer
        TextProc [label="Text Processing/LangChain", fillcolor="#4169e1"];
        CredMgr [label="Credential Manager", fillcolor="#daa520"];
        
        # Core Components
        OpenAI [label="OpenAI Embeddings", fillcolor="#4169e1"];
        Search [label="Search Interface", fillcolor="#ff69b4"];
        SQLite [label="Local SQLite DB\n(Credentials Storage)", fillcolor="#663399", shape=cylinder, height=0.6];
        
        # Storage Layer
        MongoDB [label="MongoDB Atlas\n(Vector & Document Store)", fillcolor="#2e8b57", shape=cylinder, height=0.6];
        
        # Connections
        UI -> DocUpload;
        UI -> Settings;
        UI -> Search;
        
        DocUpload -> TextProc;
        Settings -> CredMgr;
        
        TextProc -> OpenAI;
        CredMgr -> SQLite;
        OpenAI -> MongoDB;
        Search -> MongoDB;
        CredMgr -> MongoDB;
        
        # Ranks for layout
        {rank=same; DocUpload Settings}
        {rank=same; TextProc CredMgr}
        {rank=same; OpenAI Search SQLite}
    }
    """, use_container_width=True)

with arch_right:
    st.markdown("#### Database Schema")
    st.markdown("""
    <div style="text-align: right; color: #666; margin-bottom: 10px;">Click diagram to enlarge</div>
    """, unsafe_allow_html=True)
    
    st.graphviz_chart("""
    digraph {
        bgcolor="#0E1117";
        rankdir=TB;
        graph [size="5.5,5.5"];
        node [style=filled, fontcolor=white, fontname="Arial", shape=box, fontsize=11, margin=0.2, width=2, height=0.5];
        edge [color="#4169e1", penwidth=1, arrowsize=0.8];
        
        # Collections
        Documents [
            label="MongoDB: Documents Collection\n=======================\n_id: ObjectId\nfilename: string\ncreated_at: datetime\nfile_type: string\nstatus: string",
            fillcolor="#2e8b57",
            width=3,
            height=1.2
        ];
        
        Chunks [
            label="MongoDB: Chunks Collection\n=======================\n_id: ObjectId\ndoc_id: ObjectId\ntext: string\nembedding: vector\nchunk_index: int",
            fillcolor="#2e8b57",
            width=3,
            height=1.2
        ];
        
        Credentials [
            label="SQLite: Credentials DB\n=======================\n_id: integer\nservice: string\ntoken: encrypted\nupdated_at: datetime",
            fillcolor="#663399",
            width=3,
            height=1.2
        ];
        
        # Layout
        {rank=same; Documents Credentials}
        
        # Relationships
        Documents -> Chunks [label="1:n"];
    }
    """, use_container_width=True)

# Custom styling
st.markdown("""
<style>
.hero-container {
    padding: 2rem 0;
    text-align: center;
    background: linear-gradient(to right, #1e3c72, #2a5298);
    border-radius: 10px;
    margin-bottom: 2rem;
    color: white;
}

.hero-container h1 {
    font-size: 3.5rem !important;
    margin-bottom: 1rem !important;
}

.hero-subtitle {
    font-size: 1.5rem !important;
    opacity: 0.9;
}

/* Make expanders more compact */
.streamlit-expanderHeader {
    font-size: 1.1rem !important;
    padding: 0.5rem !important;
}

.streamlit-expanderContent {
    padding: 1rem !important;
}

/* Link styling */
a {
    color: #2a5298;
    text-decoration: none;
    font-weight: bold;
}

a:hover {
    text-decoration: underline;
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    padding: 0.5rem 1rem;
}
</style>
""", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    Made with ❤️ using Streamlit, OpenAI, MongoDB, and SQLite3
</div>
""", unsafe_allow_html=True) 