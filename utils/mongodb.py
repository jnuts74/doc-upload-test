from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

class MongoDB:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGODB_URI'))
        self.db = self.client['document_store']
        self.collection = self.db['documents']

    def store_document(self, document_data):
        """
        Store a document with its vector embeddings
        """
        return self.collection.insert_one(document_data)

    def get_all_documents(self):
        """
        Retrieve all documents from the collection
        """
        return list(self.collection.find())

    def close(self):
        """
        Close the MongoDB connection
        """
        self.client.close()

# Create a singleton instance
mongodb = MongoDB() 