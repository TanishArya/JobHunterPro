#!/bin/bash

echo "Setting up Job Finder application..."

# Create necessary directories if they don't exist
mkdir -p .streamlit

# Check if config.toml exists, if not create it
if [ ! -f .streamlit/config.toml ]; then
    echo "Creating Streamlit configuration..."
    cat > .streamlit/config.toml << EOL
[server]
headless = true
address = "0.0.0.0"
port = 5000

[theme]
primaryColor = "#0066CC"
secondaryColor = "#28A745"
backgroundColor = "#F8F9FA"
textColor = "#212529"
font = "Inter"
EOL
    echo "Streamlit configuration created."
fi

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Setup complete! Run 'streamlit run app.py' to start the application."