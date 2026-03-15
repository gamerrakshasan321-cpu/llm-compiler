# How to Start the Backend Server

## Quick Start

1. **Open a new PowerShell or Command Prompt window**

2. **Navigate to the backend directory:**
   ```powershell
   cd "C:\Users\L o V e\Downloads\code-companion-ai-main\code-companion-ai-main\code-companion-ai-main\backend"
   ```
   
   Or if you're already in the project root:
   ```powershell
   cd code-companion-ai-main\backend
   ```

3. **Create .env file (if it doesn't exist):**
   ```powershell
   @"
   GEMINI_API_KEY=AIzaSyDAvXrd-hIRgTDVHcAGT6UnFJA2pSHTLjA
   PORT=8000
   ENVIRONMENT=development
   "@ | Out-File -FilePath .env -Encoding utf8
   ```

4. **Install dependencies (first time only):**
   ```powershell
   pip install fastapi uvicorn python-dotenv pydantic google-generativeai python-multipart requests
   ```

5. **Start the server:**
   ```powershell
   python main.py
   ```

6. **Verify it's running:**
   - Open http://localhost:8000 in your browser
   - You should see: `{"status":"online","service":"AI Compiler Debugging Assistant API","version":"1.0.0"}`

## Alternative: Use the Batch File

Simply double-click `start-backend.bat` in the project root directory.

## Troubleshooting

- **Port 8000 already in use:** Change PORT in .env to another port (e.g., 8001)
- **Module not found:** Run `pip install -r requirements.txt` again
- **API Key error:** Make sure .env file exists and contains GEMINI_API_KEY

## The server will keep running until you press Ctrl+C


