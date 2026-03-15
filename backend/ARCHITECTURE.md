# Backend Architecture Documentation

## Overview

This backend implements a secure, modular AI-powered compiler debugging system that analyzes C and Java programs for compile-time errors, runtime errors, and logical output mismatches, generating human-readable explanations using Google Gemini API.

## Architecture

### Modular Design

The backend follows a clean, modular architecture with separation of concerns:

```
backend/
├── main.py              # FastAPI application entry point
├── config.py           # Configuration management
├── logging_config.py   # Logging setup
├── api/                # API layer
│   ├── models.py      # Pydantic request/response models
│   └── routes.py      # API endpoints
└── services/          # Business logic layer
    ├── analyzer.py    # Main orchestration service
    ├── compiler.py    # Compilation service
    ├── executor.py    # Execution service
    └── llm_service.py # LLM integration service
```

## Components

### 1. API Layer (`api/`)

**models.py**: Defines Pydantic models for request/response validation
- `AnalyzeRequest`: Input validation for analysis requests
- `AnalyzeResponse`: Structured response format
- `LLMExplanation`: LLM-generated explanation structure

**routes.py**: FastAPI route handlers
- `POST /api/analyze`: Main analysis endpoint

### 2. Services Layer (`services/`)

#### CompilerService (`compiler.py`)
- **Responsibility**: Compile C and Java source code
- **Features**:
  - C compilation using `gcc` with error capture
  - Java compilation using `javac` with error capture
  - Temporary file management
  - Timeout protection (30 seconds)
  - Error and warning parsing

#### ExecutorService (`executor.py`)
- **Responsibility**: Execute compiled programs safely
- **Features**:
  - C program execution
  - Java program execution
  - Input handling via stdin
  - Output capture (stdout/stderr)
  - Timeout protection (10 seconds)
  - Output size limits (10MB) to prevent memory issues

#### LLMService (`llm_service.py`)
- **Responsibility**: Generate AI-powered error explanations
- **Features**:
  - Google Gemini API integration
  - Structured prompt generation
  - Response parsing and validation
  - Fallback error handling

#### CodeAnalyzer (`analyzer.py`)
- **Responsibility**: Orchestrate the complete analysis workflow
- **Workflow**:
  1. Compile code
  2. Execute if compilation successful
  3. Compare output if expected output provided
  4. Generate LLM explanation

## Security Features

1. **API Key Management**: Stored in `.env` file (not in git)
2. **Execution Timeouts**: Prevents infinite loops
3. **Output Size Limits**: Prevents memory exhaustion
4. **Temporary File Cleanup**: Automatic cleanup of compiled files
5. **Input Validation**: Pydantic models validate all inputs
6. **Error Handling**: Comprehensive error handling at all levels

## API Flow

```
Client Request
    ↓
POST /api/analyze
    ↓
Route Handler (routes.py)
    ↓
CodeAnalyzer.analyze()
    ↓
    ├─→ CompilerService.compile()
    │   └─→ gcc/javac subprocess
    │
    ├─→ ExecutorService.execute() (if compile success)
    │   └─→ program subprocess
    │
    ├─→ Output comparison (if expected_output provided)
    │
    └─→ LLMService.generate_explanation()
        └─→ Google Gemini API
    ↓
Response to Client
```

## Error Handling Strategy

1. **Compilation Errors**: Captured and parsed from compiler stderr
2. **Runtime Errors**: Captured from program stderr and return codes
3. **LLM Errors**: Fallback explanations if API fails
4. **Timeout Errors**: Handled gracefully with informative messages
5. **Validation Errors**: HTTP 400 with detailed error messages

## Configuration

All configuration is managed through:
- `.env` file for sensitive data (API keys)
- `config.py` for application settings
- Environment variables for deployment flexibility

## Testing

Use `test_api.py` to verify the API:
```bash
python test_api.py
```

Tests cover:
- C compilation errors
- Java runtime errors
- Output mismatch detection

## Deployment Considerations

1. **Production Settings**:
   - Set `ENVIRONMENT=production` in `.env`
   - Configure specific CORS origins
   - Use production WSGI server (gunicorn/uvicorn with workers)
   - Set up proper logging

2. **Security**:
   - Never commit `.env` file
   - Use environment variables in production
   - Implement rate limiting
   - Add authentication if needed

3. **Performance**:
   - Consider async execution for long-running analyses
   - Implement caching for repeated code analysis
   - Monitor API rate limits for Gemini

4. **Scalability**:
   - Can be containerized with Docker
   - Stateless design allows horizontal scaling
   - Consider queue system for high load

## Future Enhancements

- Support for more languages (Python, C++, etc.)
- Code quality metrics
- Multiple test case support
- Batch processing
- WebSocket support for real-time updates
- Database for storing analysis history


