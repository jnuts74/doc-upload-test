import logging
import os
from pathlib import Path
from datetime import datetime

def setup_logger():
    """Configure logging for the application"""
    # Get project root directory
    project_root = Path(__file__).parent.parent
    logs_dir = project_root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a timestamp for the log file
    timestamp = datetime.now().strftime("%Y%m%d")
    log_file = logs_dir / f"app_{timestamp}.log"
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()  # Also log to console
        ]
    )
    
    # Create logger
    logger = logging.getLogger('doc_upload')
    return logger

# Create a singleton logger instance
logger = setup_logger() 