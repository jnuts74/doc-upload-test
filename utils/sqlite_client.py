import sqlite3
from pathlib import Path
from utils.logger import logger

class SQLiteClient:
    def __init__(self):
        # Get the project root directory (parent of utils)
        self.project_root = Path(__file__).parent.parent
        self.db_path = self.project_root / "data" / "credentials.db"
        
        # Ensure the data directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize the database
        self._init_db()
    
    def _init_db(self):
        """Initialize the SQLite database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS credentials (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL
                    )
                """)
                conn.commit()
                logger.info("SQLite database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing SQLite database: {e}")
            raise
    
    def get_credentials(self):
        """Get stored API credentials"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT key, value FROM credentials")
                results = cursor.fetchall()
                
                # Convert results to dictionary
                credentials = {}
                for key, value in results:
                    credentials[key] = value
                
                # Return None if no credentials found
                if not credentials:
                    return None
                    
                # Check if we have both required credentials
                if 'mongodb_uri' in credentials and 'openai_api_key' in credentials:
                    return credentials
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving credentials from SQLite: {e}")
            return None
    
    def save_credentials(self, mongodb_uri, openai_api_key):
        """Save API credentials"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Use REPLACE to update if exists or insert if not
                cursor.execute("""
                    REPLACE INTO credentials (key, value)
                    VALUES ('mongodb_uri', ?)
                """, (mongodb_uri,))
                cursor.execute("""
                    REPLACE INTO credentials (key, value)
                    VALUES ('openai_api_key', ?)
                """, (openai_api_key,))
                conn.commit()
                logger.info("Credentials saved successfully")
                return True
        except Exception as e:
            logger.error(f"Error saving credentials to SQLite: {e}")
            return False
    
    def clear_credentials(self):
        """Clear all stored credentials"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM credentials")
                conn.commit()
                logger.info("Credentials cleared successfully")
                return True
        except Exception as e:
            logger.error(f"Error clearing credentials from SQLite: {e}")
            return False 