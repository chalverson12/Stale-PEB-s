#!/bin/bash

# Redash to Website Startup Script

echo "🚀 Starting Redash to Website Application"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3."
    exit 1
fi

# Create directories if they don't exist
echo "📁 Creating required directories..."
mkdir -p data logs

# Install dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Check configuration
echo "🔧 Checking configuration..."
python3 -c "from config import Config; print('✓ Configuration valid' if Config.validate() else '❌ Configuration invalid - please check config.py')"

if [ $? -ne 0 ]; then
    echo "❌ Configuration validation failed. Please update your settings in config.py"
    exit 1
fi

# Test Redash connection
echo "🔌 Testing Redash connection..."
python3 redash_client.py

if [ $? -ne 0 ]; then
    echo "⚠️  Redash connection test failed. Check your API key and URL."
    echo "The application will still start, but you may need to fix the configuration."
fi

# Setup cron job (optional)
read -p "📅 Do you want to setup automatic daily refresh at 10am PST? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Setting up cron job..."
    python3 setup_cron.py
fi

# Start the web application
echo "🌐 Starting web server..."
echo "Your website will be available at: http://localhost:8000"
echo "Press Ctrl+C to stop the server"
echo

python3 app.py