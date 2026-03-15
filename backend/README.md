# AI Compiler Debugging Assistant - Backend API

A secure, modular backend for an AI-powered compiler debugging system that analyzes C and Java programs for compile-time errors, runtime errors, and logical output mismatches, generating human-readable explanations using Google Gemini API.

## Features

- ✅ Compile C and Java source code with error capture
- ✅ Execute compiled programs safely with timeouts
- ✅ Compare expected vs actual output
- ✅ AI-powered error explanations using Google Gemini
- ✅ Secure API key management via environment variables
- ✅ Production-ready error handling and logging
- ✅ RESTful API with FastAPI

## Requirements

- Python 3.9+
- gcc (for C compilation)
- javac and java (for Java compilation)
- Google Gemini API key

## Installation

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment (recommended):**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/Mac:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   - Copy `.env.example` to `.env`
   - Add your Gemini API key:
     ```
     GEMINI_API_KEY=your_api_key_here
     ```

## Running the Server

### Development Mode:
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### POST /api/analyze

Analyze code for errors and get AI-powered explanations.

**Request Body:**
```json
{
  "language": "C",
  "code": "#include <stdio.h>\nint main() { printf(\"Hello\"); return 0; }",
  "input_data": "optional input",
  "expected_output": "Hello"
}
```

**Response:**
```json
{
  "compile_errors": {
    "success": true,
    "errors": []
  },
  "runtime_errors": {
    "success": true,
    "stdout": "Hello",
    "stderr": ""
  },
  "output_analysis": {
    "match": true
  },
  "llm_explanation": {
    "summary": "Code compiled and executed successfully",
    "cause": "No errors found",
    "fix": "No fixes needed",
    "corrected_code": null
  }
}
```

### GET /

Health check endpoint.

### GET /health

Detailed health check with compiler availability.

## Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── config.py              # Configuration settings
├── logging_config.py      # Logging configuration
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not in git)
├── .env.example          # Environment variables template
├── api/
│   ├── __init__.py
│   ├── models.py         # Pydantic models
│   └── routes.py         # API routes
└── services/
    ├── __init__.py
    ├── analyzer.py       # Main analysis orchestrator
    ├── compiler.py       # Compilation service
    ├── executor.py       # Execution service
    └── llm_service.py    # Gemini API integration
```

## Security Features

- ✅ API keys stored in environment variables
- ✅ Execution timeouts to prevent infinite loops
- ✅ Output size limits to prevent memory issues
- ✅ Temporary file cleanup
- ✅ Error handling and validation
- ✅ CORS configuration

## Testing

Example C program with error:
```c
#include <stdio.h>
int main() {
    printf("Hello World\n"
    return 0;
}
```

Example Java program with error:
```java
public class Test {
    public static void main(String[] args) {
        System.out.println("Hello World"
    }
}
```

## Troubleshooting

1. **Import errors**: Ensure all dependencies are installed (`pip install -r requirements.txt`)
2. **Compiler not found**: 
   - **GCC (C compiler)**: See [INSTALL_GCC_WINDOWS.md](INSTALL_GCC_WINDOWS.md) for detailed Windows installation instructions
   - **Java JDK**: Download from https://adoptium.net/ or https://www.oracle.com/java/technologies/downloads/
   - Ensure compilers are in your PATH and restart your terminal/IDE
3. **API key errors**: Verify `.env` file exists with correct `GEMINI_API_KEY`
4. **Port already in use**: Change `PORT` in `.env` or kill the process using port 8000

## License

This project is part of an MCA final year project.

