import httpx
from openai import OpenAI
import streamlit as st
from utils.logger import logger

class OpenAIClient:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OpenAIClient, cls).__new__(cls)
            cls._instance.client = None
            cls._instance.http_client = None
        return cls._instance
    
    def connect(self):
        """Connect or reconnect to OpenAI with current credentials"""
        if not st.session_state.get('openai_api_key'):
            logger.error("OpenAI API key not found in settings")
            raise ValueError("OpenAI API key not found in settings. Please configure it in the Settings page.")
            
        try:
            if self.http_client:
                self.close()
                
            self.http_client = httpx.Client()
            self.client = OpenAI(
                api_key=st.session_state.openai_api_key,
                http_client=self.http_client
            )
            logger.info("Successfully connected to OpenAI")
        except Exception as e:
            logger.error(f"Failed to connect to OpenAI: {e}")
            raise
            
    def ensure_connection(self):
        """Ensure we have a valid connection before operations"""
        if not self.client:
            self.connect()
        return self.client
    
    def get_embedding(self, text):
        """Get embedding for a text using OpenAI's API"""
        try:
            client = self.ensure_connection()
            response = client.embeddings.create(
                input=text,
                model="text-embedding-3-small"
            )
            logger.info("Successfully generated embedding")
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
        
    def close(self):
        """Close the OpenAI connection"""
        try:
            if self.http_client:
                self.http_client.close()
                self.http_client = None
                self.client = None
                logger.info("OpenAI connection closed")
        except Exception as e:
            logger.error(f"Error closing OpenAI connection: {e}")

# Create a singleton instance
openai_client = OpenAIClient() 