# Document Upload & Vectorization App

A Streamlit application that allows users to upload documents, create vector embeddings using OpenAI, and store them in MongoDB Atlas.

## Features

- Simple web interface for document upload
- Document text chunking and vectorization using OpenAI embeddings
- MongoDB Atlas storage for documents and their embeddings
- Preview of stored documents and their chunks

## Prerequisites

- Python 3.8+
- MongoDB Atlas account and connection string
- OpenAI API key

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create and activate virtual environment:
```bash
./setup.sh
source venv/bin/activate
```

3. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key
   - Add your MongoDB Atlas connection string

4. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Activate the virtual environment (if not already activated):
```bash
source venv/bin/activate
```

2. Run the Streamlit app:
```bash
streamlit run app.py
```

3. Open your browser and navigate to the URL shown in the terminal (typically http://localhost:8501)

## Usage

1. Upload a document using the file uploader
2. Click "Upload and Process" to create embeddings and store in MongoDB
3. View processed documents and their chunks in the expandable sections below

## Project Structure

```
.
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── setup.sh           # Setup script
├── .env               # Environment variables
└── utils/
    └── mongodb.py     # MongoDB connection utilities
```

## Notes

- Supported file types: txt, pdf, doc, docx
- Documents are split into chunks of 1000 characters with 200 character overlap
- Each chunk is vectorized using OpenAI embeddings
- All data is stored in MongoDB Atlas 