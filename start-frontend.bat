@echo off
echo Starting Frontend Development Server...
echo.

REM Check if node_modules exists
if not exist node_modules (
    echo Installing dependencies...
    call npm install
    echo.
)

echo Starting frontend server on http://localhost:8080
echo Press Ctrl+C to stop
echo.

call npm run dev

pause


