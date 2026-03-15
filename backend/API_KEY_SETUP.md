# Gemini API Key Setup Guide

## Quick Diagnostic

Run this command in the backend directory to check your API key setup:

```bash
python check_api_key.py
```

This will tell you exactly what's wrong and how to fix it.

## Step-by-Step Setup

### 1. Get Your API Key

1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key" or use an existing one
4. Copy the API key (it starts with `AIza...`)

### 2. Create .env File

**Location:** Create a file named `.env` in the `backend` directory

**Full path example:**
- Windows: `C:\Users\YourName\Downloads\code-companion-ai-main\code-companion-ai-main\backend\.env`
- Mac/Linux: `~/Downloads/code-companion-ai-main/code-companion-ai-main/backend/.env`

### 3. Add API Key to .env File

Open the `.env` file in a text editor and add:

```
GEMINI_API_KEY=your_actual_api_key_here
```

**IMPORTANT FORMATTING RULES:**
- ✅ **CORRECT:** `GEMINI_API_KEY=AIzaSy...your_key`
- ❌ **WRONG:** `GEMINI_API_KEY = AIzaSy...` (spaces around =)
- ❌ **WRONG:** `GEMINI_API_KEY='AIzaSy...'` (quotes)
- ❌ **WRONG:** `GEMINI_API_KEY="AIzaSy..."` (quotes)
- ❌ **WRONG:** `GEMINI_API_KEY = "AIzaSy..."` (spaces + quotes)

**Example:**
```
GEMINI_API_KEY=AIzaSyDAvXrd-hIRgTDVHcAGT6UnFJA2pSHTLjA
PORT=8000
ENVIRONMENT=development
```

### 4. Verify Setup

Run the diagnostic script:

```bash
cd backend
python check_api_key.py
```

If everything is correct, you'll see:
```
✅ ALL CHECKS PASSED!
   Your Gemini API key is configured correctly.
```

### 5. Restart Backend Server

After setting up the API key, **restart your backend server**:

1. Stop the current server (Ctrl+C)
2. Start it again: `python main.py`

## Common Issues

### Issue: ".env file not found"
**Solution:** Make sure the `.env` file is in the `backend` directory, not the root directory.

### Issue: "API key not loaded"
**Solution:** 
- Check for spaces around the `=` sign
- Remove any quotes around the API key
- Make sure there are no extra spaces at the beginning/end of the line

### Issue: "Invalid API key"
**Solution:**
- Verify the API key is correct at https://makersuite.google.com/app/apikey
- Make sure the API key hasn't expired
- Check that you copied the entire key (they're usually long)

### Issue: "Packages not installed"
**Solution:**
```bash
pip install google-genai google-generativeai
```

## Still Having Issues?

1. Run `python check_api_key.py` and read the output carefully
2. Check the backend logs when you start the server
3. Verify the `.env` file location matches where Python is running from
4. Make sure you restarted the backend server after creating/editing `.env`

## File Structure

Your project should look like this:

```
code-companion-ai-main/
├── backend/
│   ├── .env              ← API key goes here!
│   ├── main.py
│   ├── check_api_key.py  ← Run this to diagnose
│   └── ...
└── ...
```

The `.env` file should be **inside** the `backend` folder, at the same level as `main.py`.


