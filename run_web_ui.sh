#!/bin/bash

# ============================================
# Email Threat Protection Dashboard Launcher
# Quick start script for the web UI
# ============================================

echo "============================================"
echo "🚀 Email Threat Protection Dashboard"
echo "============================================"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "✓ Python 3 found"

# Check if Flask is installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo ""
    echo "⚠️  Flask is not installed"
    echo "Installing Flask and Flask-CORS..."
    pip3 install flask flask-cors
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install Flask"
        echo "Please run: pip3 install flask flask-cors"
        exit 1
    fi
    echo "✓ Flask installed"
fi

echo "✓ Flask found"
echo ""

# Check if web_ui directory exists
if [ ! -d "web_ui" ]; then
    echo "❌ web_ui directory not found"
    echo "Please ensure you're in the correct directory"
    exit 1
fi

echo "✓ Web UI files found"
echo ""

# Start the server
echo "Starting web server..."
echo ""
echo "============================================"
echo "📱 Dashboard will be available at:"
echo "   http://localhost:5001/login.html"
echo ""
echo "Press Ctrl+C to stop the server"
echo "============================================"
echo ""

python3 web_backend.py
