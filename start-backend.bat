@echo off
REM Windows batch script to run the backend server

echo ========================================
echo Starting Backend Server
echo ========================================
echo.

REM Navigate to backend directory
cd /d "%~dp0code-companion-ai-main\backend"
if errorlevel 1 (
    echo Error: Could not find backend directory!
    echo Current directory: %CD%
    pause
    exit /b 1
)

echo Current directory: %CD%
echo.

REM Check if .env exists
if not exist .env (
    echo Creating .env file...
    (
        echo GEMINI_API_KEY=AIzaSyDAvXrd-hIRgTDVHcAGT6UnFJA2pSHTLjA
        echo PORT=8000
        echo ENVIRONMENT=development
    ) > .env
    echo .env file created successfully!
    echo.
)

REM Check if dependencies are installed
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo Installing Python dependencies...
    echo This may take a few minutes...
    pip install fastapi uvicorn python-dotenv pydantic google-generativeai python-multipart requests
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install dependencies!
        echo Please install them manually: pip install -r requirements.txt
        pause
        exit /b 1
    )
    echo.
    echo Dependencies installed successfully!
    echo.
)

echo ========================================
echo Starting server on http://localhost:8000
echo ========================================
echo.
echo Press Ctrl+C to stop the server
echo.

python main.py

pause
