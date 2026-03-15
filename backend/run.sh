#!/bin/bash
# Linux/Mac shell script to run the backend server

echo "Starting AI Compiler Debugging Assistant Backend..."
echo ""

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Check if dependencies are installed
python -c "import fastapi" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found!"
    echo "Please create .env file with your GEMINI_API_KEY"
    echo "You can run: python setup.py"
    exit 1
fi

# Run the server
echo "Starting server on http://localhost:8000"
echo "Press Ctrl+C to stop"
echo ""
python main.py


