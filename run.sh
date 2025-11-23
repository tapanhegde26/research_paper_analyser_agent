#!/bin/bash

# Research Paper Analyzer Agent - Run Script

cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import google.generativeai" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    echo "✓ Dependencies installed"
fi

# Check for API key
if [ -z "$GOOGLE_API_KEY" ]; then
    if [ -f ".env" ]; then
        export $(cat .env | grep GOOGLE_API_KEY | xargs)
    fi
    
    if [ -z "$GOOGLE_API_KEY" ]; then
        echo "⚠️  WARNING: GOOGLE_API_KEY not set!"
        echo "   Set it with: export GOOGLE_API_KEY='your_key_here'"
        echo "   Or create a .env file with: GOOGLE_API_KEY=your_key_here"
        echo ""
    fi
fi

# Run the application
echo "🚀 Starting Research Paper Analyzer Agent..."
echo ""
python src/main.py


