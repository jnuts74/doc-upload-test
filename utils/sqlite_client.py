import sqlite3
from pathlib import Path
from utils.logger import logger
from cryptography.fernet import Fernet
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os

class SQLiteClient:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SQLiteClient, cls).__new__(cls)
            cls._instance.client = None
            cls._instance._init_encryption()
        return cls._instance
    
    def __init__(self):
        # Get the project root directory (parent of utils)
        self.project_root = Path(__file__).parent.parent
        self.secure_dir = self.project_root / "data" / "secure"
        self.db_path = self.secure_dir / "credentials.db"
        self.key_path = self.secure_dir / ".key"
        
        # Ensure the secure directory exists with proper permissions
        self.secure_dir.mkdir(parents=True, exist_ok=True)
        os.chmod(self.secure_dir, 0o700)  # Restrictive permissions
        
        # Initialize the database
        self._init_db()
    
    def _init_encryption(self):
        """Initialize or load encryption key"""
        try:
            if self.key_path.exists():
                # Load existing key
                with open(self.key_path, 'rb') as key_file:
                    self.key = key_file.read()
            else:
                # Generate new key
                salt = os.urandom(16)
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=480000,
                )
                # Use machine-specific info as base for key
                machine_info = f"{os.uname().nodename}{os.uname().machine}"
                key = base64.urlsafe_b64encode(kdf.derive(machine_info.encode()))
                
                # Save key securely
                with open(self.key_path, 'wb') as key_file:
                    key_file.write(key)
                os.chmod(self.key_path, 0o600)  # Read/write for owner only
                self.key = key
                
            self.cipher_suite = Fernet(self.key)
            logger.info("Encryption initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing encryption: {e}")
            raise
    
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
                    credentials[key] = self._decrypt(encrypted_value)
                
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