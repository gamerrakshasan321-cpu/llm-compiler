"""
API routes for the compiler debugging system.
"""

from fastapi import APIRouter, HTTPException
from api.models import AnalyzeRequest, AnalyzeResponse, ErrorResponse
from services.analyzer import CodeAnalyzer
from services.llm_service import LLMService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_code(request: AnalyzeRequest):
    """
    Analyze code for compile-time errors, runtime errors, and logical mismatches.
    
    - **language**: Programming language ('C' or 'Java')
    - **code**: Source code to analyze
    - **input_data**: Optional input for program execution
    - **expected_output**: Optional expected output for comparison
    """
    try:
        # Validate language (accept both "C"/"Java" and "C"/"JAVA")
        language_upper = request.language.upper()
        if language_upper not in ["C", "JAVA"]:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported language: {request.language}. Supported languages: C, Java"
            )
        
        # Initialize analyzer
        analyzer = CodeAnalyzer()
        
        # Perform analysis
        result = await analyzer.analyze(
            language=request.language.upper(),
            code=request.code,
            input_data=request.input_data,
            expected_output=request.expected_output
        )
        
        return AnalyzeResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing code: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal error during analysis: {str(e)}"
        )


@router.get("/llm/status")
async def check_llm_status():
    """
    Check if LLM service is available and configured.
    Returns status and guidance if not available.
    """
    try:
        import os
        from pathlib import Path
        from dotenv import load_dotenv
        
        # Explicitly load .env from backend directory
        backend_dir = Path(__file__).parent.parent
        env_file = backend_dir / ".env"
        
        # Load .env file explicitly
        if env_file.exists():
            load_dotenv(dotenv_path=env_file, override=True)
        else:
            load_dotenv(override=True)
        
        # Check if API key exists in environment
        api_key = os.getenv("GEMINI_API_KEY")
        
        llm_service = LLMService()
        
        # Check if LLM is properly initialized
        is_available = (
            llm_service.model is not None or 
            llm_service.client is not None
        ) and llm_service.api_key is not None
        
        if is_available:
            return {
                "available": True,
                "message": "LLM service is available and ready to provide AI explanations",
                "model": getattr(llm_service, 'model_name', 'gemini-pro'),
                "setup_required": False,
                "env_file_exists": env_file.exists(),
                "env_file_path": str(env_file)
            }
        else:
            # Check what's missing
            if not api_key:
                return {
                    "available": False,
                    "message": "LLM service is not configured. GEMINI_API_KEY is missing.",
                    "setup_required": True,
                    "env_file_exists": env_file.exists(),
                    "env_file_path": str(env_file),
                    "setup_guide": {
                        "step1": "Get a Gemini API key from Google AI Studio: https://makersuite.google.com/app/apikey",
                        "step2": f"Create a .env file in the backend directory: {env_file}",
                        "step3": "Add the following line to .env (NO spaces, NO quotes): GEMINI_API_KEY=your_api_key_here",
                        "step4": "Restart the backend server",
                        "note": "Run 'python check_api_key.py' in the backend directory to diagnose issues"
                    }
                }
            else:
                # API key exists but model not initialized - might be import issue or invalid key
                try:
                    import google.genai as genai_new
                    has_new_api = True
                except ImportError:
                    try:
                        import google.generativeai as genai_old
                        has_new_api = False
                    except ImportError:
                        return {
                            "available": False,
                            "message": "LLM packages not installed",
                            "setup_required": True,
                            "env_file_exists": env_file.exists(),
                            "env_file_path": str(env_file),
                            "api_key_found": True,
                            "setup_guide": {
                                "step1": "Install LLM packages: pip install google-genai google-generativeai",
                                "step2": "Restart the backend server",
                                "step3": "Run 'python check_api_key.py' to verify installation"
                            }
                        }
                
                # Try to test the API key
                try:
                    if has_new_api:
                        test_client = genai_new.Client(api_key=api_key)
                    else:
                        genai_old.configure(api_key=api_key)
                        test_model = genai_old.GenerativeModel('gemini-pro')
                    
                    return {
                        "available": False,
                        "message": "API key found but LLM service not initialized. This may be a configuration issue.",
                        "setup_required": True,
                        "env_file_exists": env_file.exists(),
                        "env_file_path": str(env_file),
                        "api_key_found": True,
                        "setup_guide": {
                            "step1": "Run diagnostic script: python check_api_key.py",
                            "step2": "Check backend logs for detailed error messages",
                            "step3": "Verify API key format in .env file (no spaces, no quotes)",
                            "step4": "Restart the backend server"
                        }
                    }
                except Exception as test_error:
                    return {
                        "available": False,
                        "message": f"API key found but invalid or unauthorized: {str(test_error)}",
                        "setup_required": True,
                        "env_file_exists": env_file.exists(),
                        "env_file_path": str(env_file),
                        "api_key_found": True,
                        "error_details": str(test_error),
                        "setup_guide": {
                            "step1": "Verify your API key is correct at: https://makersuite.google.com/app/apikey",
                            "step2": "Check .env file format: GEMINI_API_KEY=your_key (no spaces, no quotes)",
                            "step3": "Run diagnostic script: python check_api_key.py",
                            "step4": "Restart the backend server"
                        }
                    }
                
    except Exception as e:
        logger.error(f"Error checking LLM status: {str(e)}", exc_info=True)
        return {
            "available": False,
            "message": f"Error checking LLM status: {str(e)}",
            "setup_required": True,
            "setup_guide": {
                "step1": "Check backend logs for detailed error information",
                "step2": "Ensure GEMINI_API_KEY is set in .env file",
                "step3": "Install dependencies: pip install -r requirements.txt",
                "step4": "Run diagnostic script: python check_api_key.py"
            }
        }

