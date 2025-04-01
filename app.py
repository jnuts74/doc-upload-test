import streamlit as st
from openai import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from utils.mongodb import mongodb
import os
from dotenv import load_dotenv
import httpx
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure Streamlit page
st.set_page_config(
    page_title="Document Search",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    /* Main content area */
    .main {
        background-color: var(--background-color);
    }
    
    /* Input boxes */
    .stTextInput input, .stTextArea textarea {
        background-color: var(--input-background-color) !important;
        color: var(--text-color) !important;
        border: 1px solid var(--border-color) !important;
    }
    
    /* Buttons */
    .stButton>button {
        width: 100%;
        margin-top: 10px;
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        cursor: pointer;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    
    /* Sidebar */
    .sidebar .sidebar-content {
        background-color: var(--sidebar-background-color);
        padding: 20px;
    }
    
    /* File uploader */
    .stFileUploader {
        background-color: var(--input-background-color);
        border-radius: 5px;
        padding: 10px;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: var(--input-background-color);
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 5px;
    }
    
    /* Search box container */
    .search-container {
        background-color: var(--input-background-color);
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 20px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize OpenAI client with custom http client
http_client = httpx.Client()
client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
    http_client=http_client
)

def get_embedding(text):
    """Get embedding for a text using OpenAI's API"""
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def process_document(file_content, filename):
    """Process the uploaded document and create embeddings"""
    # Convert bytes to string
    text = file_content.decode('utf-8')
    
    # Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    
    # Create embeddings for each chunk
    chunk_embeddings = []
    for chunk in chunks:
        embedding = get_embedding(chunk)
        chunk_embeddings.append({
            'text': chunk,
            'embedding': embedding
        })
    
    # Store in MongoDB if available
    if mongodb:
        try:
            document_data = {
                'filename': filename,
                'chunks': chunk_embeddings,
                'created_at': datetime.now()
            }
            mongodb.store_document(document_data)
        except Exception as e:
            st.error(f"Error storing document in MongoDB: {str(e)}")
            return len(chunks), False
    
    return len(chunks), True

def main():
    # Sidebar
    with st.sidebar:
        st.markdown("### 📤 Document Upload")
        uploaded_file = st.file_uploader("Choose a document", type=['txt', 'pdf', 'doc', 'docx'])
        
        if uploaded_file is not None:
            if st.button("Process Document", type="primary"):
                with st.spinner("Processing document..."):
                    try:
                        file_content = uploaded_file.read()
                        num_chunks, success = process_document(file_content, uploaded_file.name)
                        if success:
                            st.success(f"Successfully processed document into {num_chunks} chunks!")
                        else:
                            st.warning(f"Document processed into {num_chunks} chunks but failed to store in MongoDB.")
                    except Exception as e:
                        st.error(f"Error processing document: {str(e)}")
        
        st.markdown("---")
        st.markdown("### 📚 Recent Documents")
        
        if mongodb:
            try:
                documents = mongodb.get_all_documents()
                if documents:
                    # Show only the 5 most recent documents
                    for doc in documents[-5:]:
                        with st.expander(f"📄 {doc['filename']}"):
                            st.write(f"Number of chunks: {len(doc['chunks'])}")
                            st.write("First chunk preview:")
                            st.text(doc['chunks'][0]['text'][:200] + "...")
                else:
                    st.info("No documents stored yet. Upload a document to get started!")
            except Exception as e:
                st.error(f"Error retrieving documents: {str(e)}")
        else:
            st.warning("⚠️ MongoDB connection is not available.")

    # Main content
    st.markdown("""
        <h1 style='text-align: center; color: var(--primary-color);'>
            🔍 Document Search & Vectorization
        </h1>
        <p style='text-align: center; color: var(--text-color);'>
            Test application for document upload and vector search using MongoDB Atlas
        </p>
    """, unsafe_allow_html=True)
    
    # Search input in the center
    search_col1, search_col2, search_col3 = st.columns([1, 2, 1])
    with search_col2:
        st.markdown("""
            <div class='search-container'>
                <h3 style='color: var(--primary-color);'>🔍 Search Documents</h3>
            </div>
        """, unsafe_allow_html=True)
        search_query = st.text_input("Enter your search query", placeholder="Type your search here...")
        
        if search_query:
            st.info("Search functionality coming soon!")
            # TODO: Implement search functionality using vector similarity

if __name__ == "__main__":
    main() 