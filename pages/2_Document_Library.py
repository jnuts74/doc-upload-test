import streamlit as st
from utils.mongodb import mongodb
from datetime import datetime
import json

st.set_page_config(
    page_title="Document Library",
    page_icon="📚",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    /* Main content area */
    .main {
        background-color: var(--background-color);
    }
    
    /* Document cards */
    .document-card {
        background-color: var(--input-background-color);
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s;
        cursor: pointer;
    }
    
    .document-card:hover {
        transform: translateY(-5px);
    }
    
    /* Modal */
    .modal {
        display: none;
        position: fixed;
        z-index: 1000;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0,0,0,0.5);
    }
    
    .modal-content {
        background-color: var(--input-background-color);
        margin: 5% auto;
        padding: 20px;
        border-radius: 10px;
        width: 80%;
        max-height: 80vh;
        overflow-y: auto;
        position: relative;
    }
    
    .close-button {
        position: absolute;
        right: 20px;
        top: 10px;
        font-size: 28px;
        cursor: pointer;
        color: var(--text-color);
    }
    
    /* Document metadata */
    .metadata {
        color: var(--text-color);
        font-size: 0.9em;
        margin-top: 10px;
    }
    
    /* Document preview */
    .preview {
        color: var(--text-color);
        margin-top: 10px;
        font-style: italic;
    }
    
    /* Grid layout */
    .grid-container {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 20px;
        padding: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# JavaScript for modal functionality
st.markdown("""
    <script>
    function openModal(documentId) {
        document.getElementById(documentId).style.display = "block";
    }
    
    function closeModal(documentId) {
        document.getElementById(documentId).style.display = "none";
    }
    
    // Close modal when clicking outside
    window.onclick = function(event) {
        if (event.target.classList.contains('modal')) {
            event.target.style.display = "none";
        }
    }
    </script>
""", unsafe_allow_html=True)

st.title("📚 Document Library")

# Search and filter options
col1, col2 = st.columns([2, 1])
with col1:
    search_query = st.text_input("🔍 Search documents", placeholder="Search by filename or content...")
with col2:
    sort_by = st.selectbox(
        "Sort by",
        ["Newest First", "Oldest First", "Filename (A-Z)", "Filename (Z-A)"]
    )

# Get documents from MongoDB
if mongodb:
    try:
        documents = mongodb.get_all_documents()
        
        # Apply search filter if query exists
        if search_query:
            search_query = search_query.lower()
            documents = [
                doc for doc in documents 
                if search_query in doc['filename'].lower() or
                any(search_query in chunk['text'].lower() for chunk in doc['chunks'])
            ]
        
        # Apply sorting
        if sort_by == "Newest First":
            documents.sort(key=lambda x: x['created_at'], reverse=True)
        elif sort_by == "Oldest First":
            documents.sort(key=lambda x: x['created_at'])
        elif sort_by == "Filename (A-Z)":
            documents.sort(key=lambda x: x['filename'].lower())
        elif sort_by == "Filename (Z-A)":
            documents.sort(key=lambda x: x['filename'].lower(), reverse=True)
        
        if documents:
            st.markdown('<div class="grid-container">', unsafe_allow_html=True)
            
            for doc in documents:
                # Create a unique ID for the modal
                modal_id = f"modal_{doc['_id']}"
                
                # Format the date
                created_at = doc['created_at'].strftime("%Y-%m-%d %H:%M")
                
                # Create the card
                st.markdown(f"""
                    <div class="document-card" onclick="openModal('{modal_id}')">
                        <h3>{doc['filename']}</h3>
                        <div class="metadata">
                            <p>📅 Uploaded: {created_at}</p>
                            <p>📄 Chunks: {len(doc['chunks'])}</p>
                        </div>
                        <div class="preview">
                            {doc['chunks'][0]['text'][:200]}...
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Create the modal
                st.markdown(f"""
                    <div id="{modal_id}" class="modal">
                        <div class="modal-content">
                            <span class="close-button" onclick="closeModal('{modal_id}')">&times;</span>
                            <h2>{doc['filename']}</h2>
                            <div class="metadata">
                                <p>📅 Uploaded: {created_at}</p>
                                <p>📄 Total Chunks: {len(doc['chunks'])}</p>
                            </div>
                            <div class="document-content">
                                {''.join(chunk['text'] for chunk in doc['chunks'])}
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No documents found. Upload some documents to get started!")
            
    except Exception as e:
        st.error(f"Error retrieving documents: {str(e)}")
else:
    st.warning("⚠️ MongoDB connection is not available.") 