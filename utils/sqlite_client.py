import sqlite3
from pathlib import Path
from utils.logger import logger
from cryptography.fernet import Fernet
import os

class SQLiteClient:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SQLiteClient, cls).__new__(cls)
            # Initialize paths first
            cls._instance.project_root = Path(__file__).parent.parent
            cls._instance.secure_dir = cls._instance.project_root / "data" / "secure"
            cls._instance.db_path = cls._instance.secure_dir / "credentials.db"
            cls._instance.key_path = cls._instance.secure_dir / ".key"
            
            # Ensure the secure directory exists with proper permissions
            cls._instance.secure_dir.mkdir(parents=True, exist_ok=True)
            os.chmod(cls._instance.secure_dir, 0o700)  # Restrictive permissions
            
            # Initialize encryption and database
            cls._instance._init_encryption()
            cls._instance._init_db()
        return cls._instance
    
    def __init__(self):
        # All initialization is done in __new__
        pass
    
    def _init_encryption(self):
        """Initialize or load encryption key"""
        try:
            # Always ensure we have a valid key
            if self.key_path.exists():
                try:
                    # Try to load and validate existing key
                    with open(self.key_path, 'rb') as key_file:
                        key = key_file.read().strip()
                        # Test if key is valid
                        Fernet(key)
                        self.key = key
                except Exception:
                    # If key is invalid, generate new one
                    logger.warning("Invalid encryption key found, generating new key")
                    self.key = Fernet.generate_key()
                    with open(self.key_path, 'wb') as key_file:
                        key_file.write(self.key)
            else:
                # Generate new key
                self.key = Fernet.generate_key()
                # Save key securely
                with open(self.key_path, 'wb') as key_file:
                    key_file.write(self.key)
            
            # Set proper permissions
            os.chmod(self.key_path, 0o600)
            
            # Initialize Fernet cipher
            self.cipher_suite = Fernet(self.key)
            logger.info("Encryption initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing encryption: {e}")
            # If anything goes wrong, try to clean up
            if hasattr(self, 'key_path') and self.key_path.exists():
                try:
                    os.remove(self.key_path)
                    logger.info("Removed invalid key file")
                except Exception:
                    pass
            raise ValueError("Failed to initialize encryption. Please restart the application.")
    
    def _init_db(self):
        """Initialize the SQLite database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS credentials (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
                # Set secure permissions on database file
                os.chmod(self.db_path, 0o600)
                logger.info("SQLite database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing SQLite database: {e}")
            raise
    
    def _encrypt(self, value: str) -> str:
        """Encrypt a value"""
        try:
            return self.cipher_suite.encrypt(value.encode()).decode()
        except Exception as e:
            logger.error(f"Error encrypting value: {e}")
            raise
    
    def _decrypt(self, encrypted_value: str) -> str:
        """Decrypt a value"""
        try:
            return self.cipher_suite.decrypt(encrypted_value.encode()).decode()
        except Exception as e:
            logger.error(f"Error decrypting value: {e}")
            raise
    
    def get_credentials(self):
        """Get stored API credentials"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT key, value FROM credentials")
                results = cursor.fetchall()
                
                # Convert results to dictionary and decrypt values
                credentials = {}
                for key, encrypted_value in results:
                    try:
                        credentials[key] = self._decrypt(encrypted_value)
                    except Exception as e:
                        logger.error(f"Error decrypting credential {key}: {e}")
                        return None
                
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
                # Encrypt values before storing
                encrypted_uri = self._encrypt(mongodb_uri)
                encrypted_key = self._encrypt(openai_api_key)
                
                # Use REPLACE to update if exists or insert if not
                cursor.execute("""
                    REPLACE INTO credentials (key, value)
                    VALUES ('mongodb_uri', ?)
                """, (encrypted_uri,))
                cursor.execute("""
                    REPLACE INTO credentials (key, value)
                    VALUES ('openai_api_key', ?)
                """, (encrypted_key,))
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

# Create a singleton instance
sqlite_client = SQLiteClient() 