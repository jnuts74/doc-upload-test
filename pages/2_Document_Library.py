import streamlit as st
from utils.mongodb import mongodb
from utils.openai_client import openai_client
from utils.styles import get_css
import os
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Document Library",
    page_icon="📚",
    layout="wide"
)

# Apply shared CSS
st.markdown(f"<style>{get_css()}</style>", unsafe_allow_html=True)

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

# Create a container for the columns
st.markdown('<div class="column-container">', unsafe_allow_html=True)

# Left column - Upload
st.markdown('<div class="column-left">', unsafe_allow_html=True)
st.markdown('<div class="glass-container">', unsafe_allow_html=True)
st.subheader("Upload Document")

# File uploader
uploaded_file = st.file_uploader("Choose a file to upload", type=["txt", "pdf", "doc", "docx"])

if uploaded_file is not None:
    try:
        # Get the project root directory
        project_root = Path(__file__).parent.parent
        uploads_dir = project_root / "data" / "uploads"
        processed_dir = project_root / "data" / "processed"
        
        # Ensure directories exist
        uploads_dir.mkdir(parents=True, exist_ok=True)
        processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Save the uploaded file
        file_path = uploads_dir / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Get text content (implement your text extraction logic here)
        text_content = "Sample text content"  # Replace with actual text extraction
        
        try:
            # Get embedding from OpenAI
            embedding = openai_client.get_embedding(text_content)
            
            # Store in MongoDB
            mongodb.store_document({
                "filename": uploaded_file.name,
                "content": text_content,
                "embedding": embedding,
                "chunks": [{"text": text_content, "embedding": embedding}]
            })
            
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
            # Clean up uploaded file if processing failed
            file_path.unlink(missing_ok=True)
            
    except Exception as e:
        st.error(f"Error saving file: {str(e)}")

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Right column - Documents
st.markdown('<div class="column-right">', unsafe_allow_html=True)
st.markdown('<div class="glass-container">', unsafe_allow_html=True)
st.subheader("Your Documents")

try:
    # Get all documents from MongoDB
    documents = mongodb.get_all_documents()

    if documents:
        for doc in documents:
            st.markdown(f"""
                <div class="card">
                    <h4>📄 {doc['filename']}</h4>
                    <p>{doc['chunks'][0]['text'][:200]}...</p>
                    <div class="metadata">
                        🕒 Uploaded: {doc.get('created_at', 'Unknown date').strftime('%Y-%m-%d %H:%M') if isinstance(doc.get('created_at'), object) else 'Unknown date'}
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("📭 No documents found. Upload some documents to get started!")

except Exception as e:
    st.error("Error loading documents. Please check your MongoDB connection in Settings.")

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Close the container
st.markdown('</div>', unsafe_allow_html=True) 