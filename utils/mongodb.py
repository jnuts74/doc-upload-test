from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import streamlit as st
from utils.logger import logger

class MongoDB:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDB, cls).__new__(cls)
            cls._instance.client = None
            cls._instance.db = None
            cls._instance.collection = None
        return cls._instance

    def connect(self):
        """Connect or reconnect to MongoDB with current credentials"""
        if not st.session_state.get('mongodb_uri'):
            logger.error("MongoDB connection string not found in settings")
            raise ConnectionFailure("MongoDB connection string not found in settings. Please configure it in the Settings page.")
            
        try:
            if self.client:
                self.close()
                
            self.client = MongoClient(st.session_state.mongodb_uri)
            # Test the connection
            self.client.admin.command('ping')
            self.db = self.client['doc_upload_db']
            self.collection = self.db['documents']
            logger.info("Successfully connected to MongoDB")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    def ensure_connection(self):
        """Ensure we have a valid connection before operations"""
        if not self.client:
            self.connect()
        return self.collection

    def store_document(self, document_data):
        """Store a document with its vector embeddings"""
        try:
            collection = self.ensure_connection()
            result = collection.insert_one(document_data)
            logger.info(f"Successfully stored document with ID: {result.inserted_id}")
            return result
        except Exception as e:
            logger.error(f"Error storing document: {e}")
            raise

    def get_all_documents(self):
        """Retrieve all documents from the collection with full details"""
        try:
            collection = self.ensure_connection()
            # Get documents and sort by created_at in descending order
            cursor = collection.find().sort('created_at', -1)
            
            # Convert cursor to list and ensure created_at is properly formatted
            documents = []
            for doc in cursor:
                # Handle documents that might not have created_at
                if 'created_at' not in doc:
                    doc['created_at'] = 'Unknown date'
                documents.append(doc)
            
            logger.info(f"Retrieved {len(documents)} documents from MongoDB")
            return documents
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            raise

    def close(self):
        """Close the MongoDB connection"""
        try:
            if self.client:
                self.client.close()
                self.client = None
                self.db = None
                self.collection = None
                logger.info("MongoDB connection closed")
        except Exception as e:
            logger.error(f"Error closing MongoDB connection: {e}")

    def delete_document(self, document_id):
        """Delete a document by its ID"""
        try:
            collection = self.ensure_connection()
            result = collection.delete_one({"_id": document_id})
            if result.deleted_count:
                logger.info(f"Successfully deleted document with ID: {document_id}")
                return True
            else:
                logger.warning(f"No document found with ID: {document_id}")
                return False
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            raise

# Create a singleton instance
mongodb = MongoDB() 