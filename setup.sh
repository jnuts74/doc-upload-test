#!/bin/bash

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Create project directory structure
mkdir -p data/uploads     # For uploaded documents
mkdir -p data/processed   # For processed documents
mkdir -p data/secure      # For credentials database
mkdir -p utils           # For utility modules
mkdir -p logs            # For application logs

# Set up permissions
chmod 700 data/secure    # Restrictive permissions for credentials
chmod 755 data/uploads   # Read-write for uploads
chmod 755 data/processed # Read-write for processed files
chmod 755 logs          # Read-write for logs

# Create empty __init__.py files to make directories into Python packages
touch utils/__init__.py
touch data/__init__.py

# Add data directories to .gitignore
echo "data/uploads/*" >> .gitignore
echo "data/processed/*" >> .gitignore
echo "data/secure/*" >> .gitignore
echo "logs/*" >> .gitignore
echo "!data/uploads/.gitkeep" >> .gitignore
echo "!data/processed/.gitkeep" >> .gitignore
echo "!data/secure/.gitkeep" >> .gitignore
echo "!logs/.gitkeep" >> .gitignore

# Create .gitkeep files to preserve directory structure
touch data/uploads/.gitkeep
touch data/processed/.gitkeep
touch data/secure/.gitkeep
touch logs/.gitkeep

# Initialize the SQLite database
echo "Initializing credentials database..."
python3 utils/init_db.py

echo "
Setup complete! 

Project structure created:
├── app.py               # Main application
├── data/               # Data directory
│   ├── uploads/        # For uploaded documents
│   ├── processed/      # For processed documents
│   └── secure/         # For credentials database
│       ├── credentials.db  # SQLite database (initialized)
│       └── .key           # Encryption key
├── utils/              # Utility modules
├── pages/              # Streamlit pages
└── logs/               # Application logs

Credentials database initialized in:
./data/secure/credentials.db

To get started:
1. Activate the virtual environment:
   source venv/bin/activate

2. Run the application:
   streamlit run app.py

3. Go to the Settings page to configure your:
   - OpenAI API key
   - MongoDB connection string
" 