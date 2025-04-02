import streamlit as st
from utils.mongodb import mongodb
from utils.openai_client import openai_client
from utils.document_processor import document_processor
from utils.styles import get_css, apply_custom_styles
from datetime import datetime
from pathlib import Path
from bson import ObjectId
import base64
import os
from utils.sqlite_client import SQLiteClient

# Get the project root directory
project_root = Path(__file__).parent.parent

# Page config
st.set_page_config(
    page_title="Document Library",
    page_icon="��",
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
    "📚 Library": "",
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

# Initialize session state for document viewing if not exists
if 'viewing_document' not in st.session_state:
    st.session_state.viewing_document = None

# Initialize SQLite and load credentials
sqlite_client = SQLiteClient()
credentials = sqlite_client.get_credentials()

# Check credentials and initialize connections
if not credentials:
    st.warning("⚠️ Please configure your API credentials in the Settings page before using the Document Library.")
    st.markdown("""
        To get started:
        1. Go to the Settings page
        2. Enter your OpenAI API key
        3. Enter your MongoDB connection string
        4. Save your settings
        
        [Go to Settings ➜](Settings)
    """)
    st.stop()

# Update session state with credentials
st.session_state['mongodb_uri'] = credentials['mongodb_uri']
st.session_state['openai_api_key'] = credentials['openai_api_key']

# Initialize MongoDB connection at the start
try:
    mongodb.connect()  # This will use the session state credentials that we just loaded
except Exception as e:
    st.error(f"Error connecting to MongoDB: {str(e)}")
    st.info("""
    Common MongoDB Connection Issues:
    - Network connectivity
    - IP whitelist settings in MongoDB Atlas
    - Database user permissions
    - Invalid connection string format
    
    Please check your settings and try again.
    [Go to Settings ➜](Settings)
    """)
    st.stop()

# Title
st.title("📚 Document Library")

# Check if we have a valid MongoDB connection
if not mongodb.is_connected():
    st.warning("⚠️ Please configure your API credentials in the Settings page before using the Document Library.")
    st.markdown("""
        To get started:
        1. Go to the Settings page
        2. Enter your OpenAI API key
        3. Enter your MongoDB connection string
        4. Save your settings
        
        [Go to Settings ➜](Settings)
    """)
    st.stop()

# Function to handle document deletion
def delete_document(doc_id):
    try:
        if mongodb.delete_document(ObjectId(doc_id)):
            st.success("Document deleted successfully!")
            st.experimental_rerun()
        else:
            st.error("Failed to delete document.")
    except Exception as e:
        st.error(f"Error deleting document: {str(e)}")

# Function to display PDF
def display_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# Function to display text file
def display_text(file_path):
    with open(file_path, "r") as f:
        content = f.read()
    st.text_area("Document Content", value=content, height=800)

# Create a container for the upload section
if not st.session_state.viewing_document:
    st.markdown('<div class="glass-container">', unsafe_allow_html=True)
    st.subheader("Upload Document")

    # File uploader
    uploaded_file = st.file_uploader("Choose a file to upload", type=["txt", "pdf"])

    if uploaded_file is not None:
        try:
            # Ensure directories exist
            uploads_dir = project_root / "data" / "uploads"
            processed_dir = project_root / "data" / "processed"
            uploads_dir.mkdir(parents=True, exist_ok=True)
            processed_dir.mkdir(parents=True, exist_ok=True)
            
            # Save the uploaded file
            file_path = uploads_dir / uploaded_file.name
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            with st.spinner("Processing document..."):
                # Extract text from document
                text_content = document_processor.extract_text(file_path)
                
                # Create text chunks
                chunks = document_processor.create_chunks(text_content)
                
                # Get embeddings for each chunk
                chunk_data = []
                for chunk in chunks:
                    embedding = openai_client.get_embedding(chunk)
                    chunk_data.append({
                        "text": chunk,
                        "embedding": embedding
                    })
                
                # Store in MongoDB
                document = {
                    "filename": uploaded_file.name,
                    "content": text_content[:1000] + "..." if len(text_content) > 1000 else text_content,  # Store preview
                    "chunks": chunk_data,
                    "created_at": datetime.utcnow()
                }
                
                mongodb.store_document(document)
                
                # Move file to processed directory
                processed_path = processed_dir / uploaded_file.name
                file_path.rename(processed_path)
                
                st.success("✅ File uploaded and processed successfully!")
                
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            if "API key" in str(e):
                st.warning("Please check your OpenAI API key in Settings.")
            elif "MongoDB" in str(e):
                st.warning("Please check your MongoDB connection string in Settings.")
            if file_path.exists():
                file_path.unlink()

    st.markdown('</div>', unsafe_allow_html=True)

# Display documents section
st.markdown("---")

try:
    # Get all documents from MongoDB
    documents = mongodb.get_all_documents()
    
    if documents:
        # If we have a document to view (either from URL or session state)
        if st.session_state.viewing_document:
            # Find the document by filename
            doc = next((d for d in documents if d['filename'] == st.session_state.viewing_document), None)
            if doc:
                # Back button and delete button in the same row
                col1, col2 = st.columns([6,1])
                with col1:
                    if st.button("← Back to Documents"):
                        st.session_state.viewing_document = None
                        st.experimental_rerun()
                with col2:
                    if st.button("🗑️ Delete", type="secondary"):
                        delete_document(doc['_id'])
                
                # Document viewer
                st.markdown(f"### 📄 {doc['filename']}")
                
                # Find the document in processed directory
                processed_path = project_root / "data" / "processed" / doc['filename']
                
                # Create tabs for different views
                doc_tab, chunks_tab = st.tabs(["📄 Document", "🔍 Processed Chunks"])
                
                with doc_tab:
                    if processed_path.exists():
                        if doc['filename'].lower().endswith('.pdf'):
                            display_pdf(processed_path)
                        else:
                            display_text(processed_path)
                    else:
                        st.error("Original document file not found in processed directory.")
                        st.markdown("### Document Content Preview")
                        st.markdown(doc.get('content', 'No content available'))
                
                with chunks_tab:
                    st.markdown("### Processed Chunks")
                    st.info("These chunks are used for semantic search and processing.")
                    for i, chunk in enumerate(doc.get('chunks', []), 1):
                        with st.expander(f"Chunk {i}"):
                            st.markdown(chunk['text'])
            else:
                st.error("Document not found!")
                st.session_state.viewing_document = None
                st.experimental_rerun()
        else:
            # Calculate number of columns (3 for desktop view)
            NUM_COLS = 3
            
            # Create rows of columns based on number of documents
            for i in range(0, len(documents), NUM_COLS):
                # Create columns for each row
                cols = st.columns(NUM_COLS)
                
                # Fill each column with a card
                for j in range(NUM_COLS):
                    idx = i + j
                    if idx < len(documents):
                        doc = documents[idx]
                        with cols[j]:
                            # Card container with custom styling
                            st.markdown("""
                            <style>
                                .document-card {
                                    background-color: #1E1E1E;
                                    border: 1px solid #333;
                                    border-radius: 8px;
                                    padding: 1.25rem;
                                    margin-bottom: 1rem;
                                }
                                .card-header {
                                    margin-bottom: 0.75rem;
                                }
                                .filename {
                                    font-weight: bold;
                                    color: #fff;
                                }
                                .card-content {
                                    color: #ccc;
                                    font-size: 0.9rem;
                                    margin-bottom: 0.75rem;
                                }
                                .card-footer {
                                    color: #888;
                                    font-size: 0.8rem;
                                    border-top: 1px solid #333;
                                    padding-top: 0.75rem;
                                    margin-top: 0.75rem;
                                }
                            </style>
                            """, unsafe_allow_html=True)
                            
                            # Determine file type and icon
                            file_type = doc.get('filename', '').split('.')[-1].upper() if '.' in doc.get('filename', '') else 'UNKNOWN'
                            file_icon = "📄" if file_type == 'TXT' else "📑"
                            
                            # Get file size
                            file_path = project_root / "data" / "processed" / doc.get('filename', '')
                            if file_path.exists():
                                file_size = file_path.stat().st_size / 1024  # Convert bytes to KB
                                if file_size > 1024:
                                    file_size_str = f"{file_size/1024:.1f} MB"
                                else:
                                    file_size_str = f"{file_size:.1f} KB"
                            else:
                                file_size_str = "0 KB"
                            
                            # Format date
                            created_at = doc.get('created_at', datetime.now())
                            date_str = created_at.strftime("%Y-%m-%d %H:%M")
                            
                            # Display card content
                            st.markdown(f"""
                            <div class="document-card">
                                <div class="card-header">
                                    <span class="filename">{file_icon} {doc.get('filename', 'Untitled')}</span>
                                </div>
                                <div class="card-content">
                                    <div>Type: {file_type}</div>
                                    <div>Size: {file_size_str}</div>
                                </div>
                                <div class="card-footer">
                                    {date_str}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Add buttons
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("👁️ View", key=f"view_{str(doc['_id'])}", use_container_width=True):
                                    st.session_state.viewing_document = str(doc['_id'])
                                    st.experimental_rerun()
                            with col2:
                                if st.button("🗑️ Delete", key=f"delete_{str(doc['_id'])}", type="primary", use_container_width=True):
                                    delete_document(doc['_id'])
    else:
        st.info("No documents found. Upload a document to get started!")
        
except Exception as e:
    st.error(f"Error loading documents: {str(e)}")
    if "MongoDB" in str(e):
        st.warning("Please check your MongoDB connection in Settings.") 