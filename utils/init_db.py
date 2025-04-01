from credentials_manager import credentials_manager
from utils.logger import logger

def init_db():
    """Initialize the credentials database and encryption"""
    try:
        # This will create the database file, tables, and encryption key
        credentials_manager._init_database()
        logger.info(f"Credentials database initialized successfully at: {credentials_manager.db_path}")
        logger.info(f"Encryption key created at: {credentials_manager.key_path}")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

if __name__ == "__main__":
    init_db() 