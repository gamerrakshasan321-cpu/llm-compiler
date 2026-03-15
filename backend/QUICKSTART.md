# Quick Start Guide

## Prerequisites

- Python 3.9 or higher
- gcc (for C compilation)
- Java JDK (for Java compilation)
- Google Gemini API key

## Installation Steps

### 1. Navigate to Backend Directory
```bash
cd backend
```

### 2. Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

**Option A: Use Setup Script**
```bash
python setup.py
```

**Option B: Manual Setup**
Create a `.env` file in the backend directory:
```
GEMINI_API_KEY=your_gemini_api_key_here
PORT=8000
ENVIRONMENT=development
```

**Note**: Your Gemini API key is: `AIzaSyDAvXrd-hIRgTDVHcAGT6UnFJA2pSHTLjA`

### 5. Run the Server

**Option A: Using Run Script**
```bash
# Windows
run.bat

# Linux/Mac
chmod +x run.sh
./run.sh
```

**Option B: Direct Python**
```bash
python main.py
```

**Option C: Using Uvicorn**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Verify Installation

1. **Check Server Status**
   ```bash
   curl http://localhost:8000/
   ```
   Or visit: http://localhost:8000

2. **Check Health**
   ```bash
   curl http://localhost:8000/health
   ```

3. **View API Documentation**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Test the API

### Using curl:

```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "language": "C",
    "code": "#include <stdio.h>\nint main() { printf(\"Hello\"); return 0; }"
  }'
```

### Using Python Test Script:

```bash
# Make sure server is running first
python test_api.py
```

### Using Python requests:

```python
import requests

response = requests.post(
    "http://localhost:8000/api/analyze",
    json={
        "language": "C",
        "code": "#include <stdio.h>\nint main() { printf(\"Hello\"); return 0; }",
        "expected_output": "Hello"
    }
)

print(response.json())
```

## Example Requests

### C Program with Compile Error:
```json
{
  "language": "C",
  "code": "#include <stdio.h>\nint main() {\n    printf(\"Hello\\n\"\n    return 0;\n}"
}
```

### Java Program with Runtime Error:
```json
{
  "language": "Java",
  "code": "public class Test {\n    public static void main(String[] args) {\n        int[] arr = new int[5];\n        System.out.println(arr[10]);\n    }\n}"
}
```

### Program with Output Mismatch:
```json
{
  "language": "C",
  "code": "#include <stdio.h>\nint main() {\n    printf(\"Hello\");\n    return 0;\n}",
  "expected_output": "Hello World"
}
```

## Troubleshooting

### Port Already in Use
```bash
# Windows: Find and kill process
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac: Find and kill process
lsof -ti:8000 | xargs kill -9
```

### Compiler Not Found
- **gcc**: Install via package manager or MinGW (Windows)
- **javac/java**: Install Java JDK

### API Key Error
- Verify `.env` file exists and contains `GEMINI_API_KEY`
- Check API key is valid at https://makersuite.google.com/app/apikey

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## Next Steps

1. Integrate with frontend (React app)
2. Configure CORS for your frontend URL
3. Set up production deployment
4. Review `ARCHITECTURE.md` for detailed documentation


