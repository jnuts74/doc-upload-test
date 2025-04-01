import streamlit as st
from utils.mongodb import mongodb
from utils.openai_client import openai_client
from utils.document_processor import document_processor
from utils.styles import get_css
from datetime import datetime
from pathlib import Path
from bson import ObjectId
import base64

# Get the project root directory
project_root = Path(__file__).parent.parent

# Page config
st.set_page_config(
    page_title="Document Library",
    page_icon="📚",
    layout="wide"
)

# Apply shared CSS
st.markdown(f"<style>{get_css()}</style>", unsafe_allow_html=True)

# Initialize session state for document viewing
if 'viewing_document' not in st.session_state:
    st.session_state.viewing_document = None

# Title
st.title("📚 Document Library")

# Check if credentials are configured
if not st.session_state.get('mongodb_uri') or not st.session_state.get('openai_api_key'):
    st.warning("⚠️ Please configure your API credentials in the Settings page before using the Document Library.")
    st.markdown("""
        To get started:
        1. Go to the Settings page
        2. Enter your OpenAI API key
        3. Enter your MongoDB connection string
        4. Save your settings
        
        [Go to Settings](Settings)
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
st.subheader("📝 Your Documents")

try:
    # Get all documents from MongoDB
    documents = mongodb.get_all_documents()
    
    if documents:
        # If viewing a specific document
        if st.session_state.viewing_document:
            doc = next((d for d in documents if str(d['_id']) == st.session_state.viewing_document), None)
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
        
        # Display document cards
        else:
            for doc in documents:
                # Format the date
                upload_date = doc['created_at']
                if upload_date != 'Unknown date':
                    try:
                        date_str = upload_date.strftime('%Y-%m-%d %H:%M')
                    except:
                        date_str = str(upload_date)
                else:
                    date_str = 'Unknown date'
                
                # Create columns for the document card and buttons
                col1, col2 = st.columns([5,1])
                
                # Document info in first column
                with col1:
                    st.markdown(f"""
                        <div class="card" style="cursor: pointer" onclick="alert('Use the View button to see document details')">
                            <h4>📄 {doc['filename']}</h4>
                            <p>{doc.get('content', 'No preview available')[:200]}...</p>
                            <div class="metadata">
                                🕒 Uploaded: {date_str}
                                | 📊 Chunks: {len(doc.get('chunks', []))}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                
                # Buttons in second column
                with col2:
                    # View button
                    if st.button("👁️ View", key=f"view_{doc['_id']}"):
                        st.session_state.viewing_document = str(doc['_id'])
                        st.experimental_rerun()
                    
                    # Delete button
                    if st.button("🗑️ Delete", key=f"delete_{doc['_id']}"):
                        delete_document(doc['_id'])
    else:
        st.info("No documents found. Upload a document to get started!")
        
except Exception as e:
    st.error(f"Error loading documents: {str(e)}")
    if "MongoDB" in str(e):
        st.warning("Please check your MongoDB connection in Settings.") 