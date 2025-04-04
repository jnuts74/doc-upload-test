import sqlite3
import os
from pathlib import Path
from cryptography.fernet import Fernet
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class CredentialsManager:
    def __init__(self):
        # Get project root directory
        self.project_root = Path(__file__).parent.parent
        
        # Create data directory if it doesn't exist
        self.data_dir = self.project_root / "data" / "secure"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Database and key paths
        self.db_path = self.data_dir / "credentials.db"
        self.key_path = self.data_dir / ".key"
        
        # Initialize encryption key
        self._init_encryption()
        
        # Initialize database
        self._init_database()
    
    def _init_encryption(self):
        """Initialize or load encryption key"""
        if not self.key_path.exists():
            # Generate a new key
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=480000,
            )
            # Use application-specific data as base for key
            app_data = str(self.project_root.absolute()).encode()
            key = base64.urlsafe_b64encode(kdf.derive(app_data))
            
            # Save key and salt
            with open(self.key_path, 'wb') as f:
                f.write(salt + key)
        
        # Load the key
        with open(self.key_path, 'rb') as f:
            data = f.read()
            salt = data[:16]
            self.key = data[16:]
        
        self.cipher = Fernet(self.key)
    
    def _init_database(self):
        """Initialize SQLite database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS credentials (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
    
    def save_credential(self, key: str, value: str):
        """Save an encrypted credential"""
        encrypted_value = self.cipher.encrypt(value.encode()).decode()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO credentials (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (key, encrypted_value))
    
    def get_credential(self, key: str) -> str:
        """Retrieve and decrypt a credential"""
        with sqlite3.connect(self.db_path) as conn:
            result = conn.execute('''
                SELECT value FROM credentials
                WHERE key = ?
            ''', (key,)).fetchone()
            
            if result:
                try:
                    return self.cipher.decrypt(result[0].encode()).decode()
                except Exception:
                    return None
            return None
    
    def delete_credential(self, key: str):
        """Delete a credential"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('DELETE FROM credentials WHERE key = ?', (key,))
    
    def clear_all(self):
        """Clear all stored credentials"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('DELETE FROM credentials')

# Create a singleton instance
credentials_manager = CredentialsManager() 