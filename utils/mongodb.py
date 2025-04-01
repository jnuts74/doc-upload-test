from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv
import os

load_dotenv()

class MongoDB:
    def __init__(self):
        try:
            self.client = MongoClient(os.getenv('MONGODB_URI'))
            # Test the connection
            self.client.admin.command('ping')
            self.db = self.client['doc_upload_db']
            self.collection = self.db['documents']
            print("Successfully connected to MongoDB!")
        except ConnectionFailure as e:
            print(f"Failed to connect to MongoDB: {e}")
            raise

    def store_document(self, document_data):
        """
        Store a document with its vector embeddings
        """
        try:
            result = self.collection.insert_one(document_data)
            print(f"Successfully stored document with ID: {result.inserted_id}")
            return result
        except Exception as e:
            print(f"Error storing document: {e}")
            raise

    def get_all_documents(self):
        """
        Retrieve all documents from the collection
        """
        try:
            return list(self.collection.find())
        except Exception as e:
            print(f"Error retrieving documents: {e}")
            raise

    def close(self):
        """
        Close the MongoDB connection
        """
        try:
            self.client.close()
            print("MongoDB connection closed")
        except Exception as e:
            print(f"Error closing MongoDB connection: {e}")

# Create a singleton instance
try:
    mongodb = MongoDB()
except Exception as e:
    print(f"Failed to initialize MongoDB: {e}")
    mongodb = None 