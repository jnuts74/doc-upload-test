import streamlit as st
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from utils.mongodb import mongodb
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Streamlit page
st.set_page_config(
    page_title="Document Upload & Vectorization",
    page_icon="📄",
    layout="wide"
)

# Initialize OpenAI embeddings
embeddings = OpenAIEmbeddings(openai_api_key=os.getenv('OPENAI_API_KEY'))

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
        embedding = embeddings.embed_query(chunk)
        chunk_embeddings.append({
            'text': chunk,
            'embedding': embedding
        })
    
    # Store in MongoDB
    document_data = {
        'filename': filename,
        'chunks': chunk_embeddings
    }
    
    mongodb.store_document(document_data)
    return len(chunks)

def main():
    st.title("📄 Document Upload & Vectorization")
    st.write("Upload a document to create vector embeddings and store in MongoDB")
    
    # File uploader
    uploaded_file = st.file_uploader("Choose a document", type=['txt', 'pdf', 'doc', 'docx'])
    
    if uploaded_file is not None:
        if st.button("Upload and Process"):
            with st.spinner("Processing document..."):
                try:
                    file_content = uploaded_file.read()
                    num_chunks = process_document(file_content, uploaded_file.name)
                    st.success(f"Successfully processed document into {num_chunks} chunks!")
                except Exception as e:
                    st.error(f"Error processing document: {str(e)}")
    
    # Display stored documents
    st.subheader("Stored Documents")
    documents = mongodb.get_all_documents()
    
    if documents:
        for doc in documents:
            with st.expander(f"📄 {doc['filename']}"):
                st.write(f"Number of chunks: {len(doc['chunks'])}")
                st.write("First chunk preview:")
                st.text(doc['chunks'][0]['text'][:200] + "...")
    else:
        st.info("No documents stored yet. Upload a document to get started!")

if __name__ == "__main__":
    main() 