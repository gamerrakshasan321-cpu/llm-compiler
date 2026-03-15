"""
Configuration settings for the application.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PORT = int(os.getenv("PORT", 8000))
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Compiler Configuration
COMPILE_TIMEOUT = 30  # seconds
EXECUTION_TIMEOUT = 10  # seconds
MAX_OUTPUT_SIZE = 10 * 1024 * 1024  # 10MB

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


