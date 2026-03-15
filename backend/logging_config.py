"""
Logging configuration for the application.
"""

import logging
import sys
from config import LOG_LEVEL

def setup_logging():
    """Configure application logging."""
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


