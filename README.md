# Document Search & Vectorization Application

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

## 🛠️ Technology Stack

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

## 🏗️ System Architecture

### Architecture Diagram
![System Architecture](https://i.imgur.com/8XZqY3N.png)

### Process Flow
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

## 📊 Database Schema

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

## 🚀 Getting Started

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file with your credentials:
   ```
   OPENAI_API_KEY=your_openai_api_key
   MONGODB_URI=your_mongodb_uri
   ```
5. Run the application:
   ```bash
   streamlit run app.py
   ```

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

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details. 