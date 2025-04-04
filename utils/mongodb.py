from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from pymongo.operations import SearchIndexModel
import streamlit as st
from utils.logger import logger
import os
import time

class MongoDB:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDB, cls).__new__(cls)
            cls._instance.client = None
            cls._instance.db = None
            cls._instance.collection = None
            cls._instance.db_name = "searchDb"
            cls._instance.collection_name = "documents"
        return cls._instance

    def is_connected(self):
        """Check if we have a valid MongoDB connection"""
        try:
            if self.client:
                # Test the connection
                self.client.admin.command('ping')
                return True
            return False
        except Exception:
            return False

    def connect(self):
        """Connect or reconnect to MongoDB with current credentials"""
        if not st.session_state.get('mongodb_uri'):
            logger.error("MongoDB connection string not found in session state")
            raise ConnectionFailure("MongoDB connection string not found. Please configure it in the Settings page.")
            
        try:
            if self.client:
                self.close()
                
            # Clean up the connection string and ensure proper database
            mongodb_uri = st.session_state.mongodb_uri.strip()
            
            # Connect to MongoDB
            self.client = MongoClient(mongodb_uri)
            
            # Test the connection
            self.client.admin.command('ping')
            
            # Initialize database and collections
            self._initialize_database()
            
            logger.info("Successfully connected to MongoDB")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    def _initialize_database(self):
        """Initialize database and create necessary indexes"""
        try:
            # Create database and collection if they don't exist
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]
            
            # Create date-based index for efficient querying
            self.collection.create_index([("created_at", 1)])
            
            # Check if vector search index already exists
            existing_indexes = list(self.collection.list_search_indexes())
            index_exists = any(idx.get("name") == "vector-search-index" for idx in existing_indexes)
            
            if not index_exists:
                # Create vector search index using the exact working template
                search_index_model = SearchIndexModel(
                    definition={
                        "fields": [{
                            "type": "vector",
                            "numDimensions": 1536,
                            "path": "chunks.embedding",
                            "similarity": "cosine"
                        }]
                    },
                    name="vector-search-index",
                    type="vectorSearch"
                )
                
                result = self.collection.create_search_index(model=search_index_model)
                logger.info(f"New search index named {result} is building.")
                
                # Wait for initial sync to complete
                logger.info("Polling to check if the index is ready. This may take up to a minute.")
                predicate = lambda index: index.get("queryable") is True
                
                while True:
                    indices = list(self.collection.list_search_indexes(result))
                    if len(indices) and predicate(indices[0]):
                        break
                    time.sleep(5)
                logger.info(f"{result} is ready for querying.")
            else:
                logger.info("Vector search index already exists")
            
        except Exception as e:
            if "IndexAlreadyExists" in str(e):
                logger.info("Vector search index already exists")
            else:
                logger.error(f"Error initializing database: {e}")
                raise

    def ensure_connection(self):
        """Ensure we have a valid connection before operations"""
        if not self.is_connected():
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

    def has_documents(self):
        """Check if there are any documents in the database."""
        try:
            return self.collection.count_documents({}) > 0
        except Exception as e:
            logger.error(f"Error checking for documents: {e}")
            return False

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

    def search_documents(self, query_embedding, limit=5):
        """Search documents using vector similarity"""
        try:
            collection = self.ensure_connection()
            
            # Aggregate pipeline for vector search
            pipeline = [
                # Match only documents that have chunks
                {
                    "$match": {
                        "chunks": {"$exists": True, "$ne": []}
                    }
                },
                
                # Unwind the chunks array to search within each chunk
                {"$unwind": "$chunks"},
                
                # Match only chunks that have embeddings
                {
                    "$match": {
                        "chunks.embedding": {"$exists": True}
                    }
                },
                
                # Add a similarity score using dot product
                {
                    "$addFields": {
                        "similarity": {
                            "$reduce": {
                                "input": {"$range": [0, {"$size": "$chunks.embedding"}]},
                                "initialValue": 0,
                                "in": {
                                    "$add": [
                                        "$$value",
                                        {"$multiply": [
                                            {"$arrayElemAt": ["$chunks.embedding", "$$this"]},
                                            {"$arrayElemAt": [query_embedding, "$$this"]}
                                        ]}
                                    ]
                                }
                            }
                        }
                    }
                },
                
                # Sort by similarity score (highest first)
                {"$sort": {"similarity": -1}},
                
                # Group back by document to get best matching chunks
                {
                    "$group": {
                        "_id": "$_id",
                        "filename": {"$first": "$filename"},
                        "content": {"$first": "$content"},
                        "created_at": {"$first": "$created_at"},
                        "similarity": {"$max": "$similarity"},
                        "best_chunk": {"$first": "$chunks.text"},
                    }
                },
                
                # Final sort of documents by best chunk similarity
                {"$sort": {"similarity": -1}},
                
                # Limit results
                {"$limit": limit}
            ]
            
            results = list(collection.aggregate(pipeline))
            
            if not results:
                logger.warning("No documents found with valid chunks and embeddings")
                return []
            
            logger.info(f"Found {len(results)} documents matching the query")
            return results
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise

# Create a singleton instance
mongodb = MongoDB() 