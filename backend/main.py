"""
Main FastAPI application for AI-powered compiler debugging system.
Handles compilation, execution, and LLM-powered error analysis.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from dotenv import load_dotenv
import os

from api.routes import router
from api.models import ErrorResponse
from logging_config import setup_logging

# Load environment variables
load_dotenv()

# Setup logging
setup_logging()

# Initialize FastAPI app
app = FastAPI(
    title="AI Compiler Debugging Assistant API",
    description="Secure backend for analyzing C and Java programs with AI-powered error explanations",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "service": "AI Compiler Debugging Assistant API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "compilers": {
            "gcc": "available",
            "javac": "available",
            "java": "available"
        },
        "llm": "gemini"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc)
        }
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )

