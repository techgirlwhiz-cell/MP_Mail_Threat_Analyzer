#!/bin/bash
# Start the web dashboard. For desktop GUI use: python3 app.py
# Run from project root (directory containing web_backend.py).

if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "Starting MailThreat Analyzer (web)..."
echo "Open: http://localhost:5001/login.html"
echo ""

python3 web_backend.py
