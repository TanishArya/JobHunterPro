#!/bin/bash

# Create .env file for environment variables if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file for environment variables..."
    cat > .env << EOF
# Database settings
DATABASE_URL=postgresql://username:password@localhost:5432/jobfinder

# Email notification settings
EMAIL_SENDER=your-email@example.com
EMAIL_PASSWORD=your-email-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EOF
    echo ".env file created. Please update with your database and email credentials."
fi

# Create .streamlit directory and config if they don't exist
if [ ! -d ".streamlit" ]; then
    echo "Creating .streamlit directory and config..."
    mkdir -p .streamlit
    cat > .streamlit/config.toml << EOF
[server]
headless = true
address = "0.0.0.0"
port = 5000

[theme]
primaryColor = "#0066CC"
backgroundColor = "#F8F9FA"
textColor = "#212529"
font = "Inter"
EOF
    echo ".streamlit/config.toml created."
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r dependencies.txt

echo "Setup complete! Run 'streamlit run app.py' to start the application."