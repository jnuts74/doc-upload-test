#!/bin/bash

echo "
🔍 S.E.A.R.C.H.
Semantic Embeddings And Retrieval Cloud Hub
----------------------------------------
"

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if (( $(echo "$python_version 3.12" | awk '{print ($1 < $2)}') )); then
    echo "❌ Error: Python 3.12 or higher is required"
    echo "Current version: $python_version"
    exit 1
fi

echo "✅ Python version $python_version detected"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "🔄 Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Set up secure storage
echo "🔒 Setting up secure storage..."
if [ ! -d "data/secure" ]; then
    mkdir -p data/secure
    chmod 700 data/secure
fi

# Set proper permissions
chmod 700 data/secure    # Restrictive permissions for credentials
chmod 755 data/uploads   # Read-write for uploads
chmod 755 data/processed # Read-write for processed files
chmod 755 static        # Read-write for static files
chmod 755 logs          # Read-write for logs

# Initialize the SQLite database
echo "🔐 Initializing secure credential storage..."
python3 utils/init_db.py

# Create or update .streamlit config
echo "⚙️ Configuring Streamlit..."
mkdir -p .streamlit
cat > .streamlit/config.toml << EOL
[theme]
primaryColor = "#4169e1"  # Royal Blue
backgroundColor = "#0e1117"  # Dark background
secondaryBackgroundColor = "#1a1f29"  # Slightly lighter dark
textColor = "#fafafa"  # Almost white
font = "sans serif"

[server]
maxUploadSize = 100
enableXsrfProtection = true
enableCORS = false

[browser]
gatherUsageStats = false
EOL

echo "
✨ Setup complete! 

To get started:

1. Activate the virtual environment:
   source venv/bin/activate

2. Run the application:
   streamlit run Home.py

3. Configure your credentials:
   - Go to the Settings page
   - Enter your OpenAI API key
   - Enter your MongoDB connection string
   - Click Save Settings

For more information, visit:
🔗 MongoDB Atlas: https://www.mongodb.com/atlas/database
🔗 OpenAI API Keys: https://platform.openai.com/api-keys

Need help? Check the README.md file for detailed documentation.
" 