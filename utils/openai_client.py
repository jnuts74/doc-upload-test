import os
import httpx
from openai import OpenAI
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()

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
            raise ValueError("OpenAI API key not found in settings. Please configure it in the Settings page.")
            
        try:
            if self.http_client:
                self.close()
                
            self.http_client = httpx.Client()
            self.client = OpenAI(
                api_key=st.session_state.openai_api_key,
                http_client=self.http_client
            )
            print("Successfully connected to OpenAI!")
        except Exception as e:
            print(f"Failed to connect to OpenAI: {e}")
            raise
            
    def ensure_connection(self):
        """Ensure we have a valid connection before operations"""
        if not self.client:
            self.connect()
        return self.client
    
    def get_embedding(self, text):
        """Get embedding for a text using OpenAI's API"""
        client = self.ensure_connection()
        response = client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        return response.data[0].embedding
        
    def close(self):
        """Close the OpenAI connection"""
        try:
            if self.http_client:
                self.http_client.close()
                self.http_client = None
                self.client = None
                print("OpenAI connection closed")
        except Exception as e:
            print(f"Error closing OpenAI connection: {e}")

# Create a singleton instance
openai_client = OpenAIClient() 