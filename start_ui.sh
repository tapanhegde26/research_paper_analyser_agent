#!/bin/bash

# Research Paper Analyzer - UI Startup Script

cd "$(dirname "$0")"

echo "🔬 Research Paper Analyzer - Web UI"
echo "======================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Creating..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Check if core dependencies are installed
if ! python -c "import google.generativeai" 2>/dev/null; then
    echo "📦 Installing all dependencies..."
    pip install -r requirements.txt
    echo "✅ Dependencies installed!"
elif ! python -c "import fastapi" 2>/dev/null; then
    echo "📦 Installing web dependencies..."
    pip install fastapi uvicorn[standard] websockets python-multipart
    echo "✅ Web dependencies installed!"
fi

# Check for API key
if [ -z "$GOOGLE_API_KEY" ]; then
    if [ -f ".env" ]; then
        export $(cat .env | grep GOOGLE_API_KEY | xargs)
    fi
    
    if [ -z "$GOOGLE_API_KEY" ]; then
        echo "⚠️  WARNING: GOOGLE_API_KEY not set!"
        echo "   Set it with: export GOOGLE_API_KEY='your_key_here'"
        echo ""
    fi
fi

echo "🚀 Starting server..."
echo ""
echo "📍 Web UI:  http://localhost:8000/ui"
echo "📍 API Docs: http://localhost:8000/docs"
echo "📍 Health:   http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start the server from project root
python src/api.py


