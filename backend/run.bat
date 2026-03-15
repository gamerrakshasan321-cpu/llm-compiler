@echo off
REM Windows batch script to run the backend server

echo Starting AI Compiler Debugging Assistant Backend...
echo.

REM Check if virtual environment exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Check if dependencies are installed
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

REM Check if .env exists
if not exist .env (
    echo Warning: .env file not found!
    echo Please create .env file with your GEMINI_API_KEY
    echo You can run: python setup.py
    pause
    exit /b 1
)

REM Run the server
echo Starting server on http://localhost:8000
echo Press Ctrl+C to stop
echo.
python main.py


