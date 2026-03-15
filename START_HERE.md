# Quick Start Guide

## Prerequisites
- Node.js and npm installed
- Python 3.9+ installed
- gcc (for C compilation)
- Java JDK (for Java compilation)

## Starting the Application

### Step 1: Start the Backend Server

Open a terminal and run:

```bash
# Navigate to backend directory
cd code-companion-ai-main/backend

# Install Python dependencies (first time only)
pip install -r requirements.txt

# Create .env file if it doesn't exist
# Add your Gemini API key:
# GEMINI_API_KEY=your_api_key_here
# PORT=8000

# Start the backend server
python main.py
```

The backend will start on **http://localhost:8000**

### Step 2: Start the Frontend

Open a **NEW** terminal window and run:

```bash
# Navigate to project root
cd code-companion-ai-main

# Install dependencies (first time only)
npm install

# Start the frontend development server
npm run dev
```

The frontend will start on **http://localhost:8080**

### Step 3: Use the Application

1. Open your browser and go to **http://localhost:8080**
2. Navigate to the Workspace page
3. Write or paste your C or Java code
4. Click "Analyze Code" to get AI-powered error analysis

## Troubleshooting

### "Failed to fetch" Error
- **Problem**: Backend server is not running
- **Solution**: Make sure the backend is running on port 8000
- Check: Open http://localhost:8000 in your browser - you should see a JSON response

### Code Editor Not Editable
- **Problem**: Z-index or CSS issue
- **Solution**: Refresh the page (Ctrl+R or Cmd+R)
- If still not working, check browser console for errors

### Backend Connection Issues
- Verify backend is running: `netstat -ano | findstr :8000` (Windows) or `lsof -i :8000` (Mac/Linux)
- Check CORS settings in `backend/main.py`
- Ensure firewall is not blocking port 8000

### API Key Error
- Make sure `.env` file exists in `backend/` directory
- Add your Gemini API key: `GEMINI_API_KEY=your_key_here`
- Restart the backend server after adding the key

## API Endpoints

- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:8080

## Need Help?

1. Check backend logs in the terminal where you started the backend
2. Check browser console (F12) for frontend errors
3. Verify both servers are running on the correct ports


