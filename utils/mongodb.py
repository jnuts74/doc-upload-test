from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import streamlit as st

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
            raise ConnectionFailure("MongoDB connection string not found in settings. Please configure it in the Settings page.")
            
        try:
            if self.client:
                self.close()
                
            self.client = MongoClient(st.session_state.mongodb_uri)
            # Test the connection
            self.client.admin.command('ping')
            self.db = self.client['doc_upload_db']
            self.collection = self.db['documents']
            print("Successfully connected to MongoDB!")
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}")
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
            print(f"Successfully stored document with ID: {result.inserted_id}")
            return result
        except Exception as e:
            print(f"Error storing document: {e}")
            raise

    def get_all_documents(self):
        """Retrieve all documents from the collection"""
        try:
            collection = self.ensure_connection()
            return list(collection.find())
        except Exception as e:
            print(f"Error retrieving documents: {e}")
            raise

    def close(self):
        """Close the MongoDB connection"""
        try:
            if self.client:
                self.client.close()
                self.client = None
                self.db = None
                self.collection = None
                print("MongoDB connection closed")
        except Exception as e:
            print(f"Error closing MongoDB connection: {e}")

# Create a singleton instance
mongodb = MongoDB() 