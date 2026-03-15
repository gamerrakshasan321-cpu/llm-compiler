"""
Test the fixed LLM service with a real compile error.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Load .env
env_file = backend_dir / ".env"
if env_file.exists():
    load_dotenv(dotenv_path=env_file, override=True)
else:
    load_dotenv(override=True)

from services.llm_service import LLMService

# Test code with compile error
test_code = """#include <stdio.h>
int main() {
    printf("Hello"
    return 0;
}
"""

print("Testing LLM Service with compile error...")
print("=" * 70)
print("\nTest Code:")
print(test_code)
print("=" * 70)

# Create LLM service
llm_service = LLMService()

# Check if initialized
if not llm_service.client and not llm_service.model:
    print("\n[X] LLM service not initialized!")
    print("   Check GEMINI_API_KEY configuration")
    sys.exit(1)

print(f"\n[OK] LLM service initialized")
print(f"   Using new API: {llm_service.use_new_api}")
print(f"   Model: {getattr(llm_service, 'model_name', 'N/A')}")

# Simulate compile errors
compile_errors = {
    "success": False,
    "errors": [
        {
            "line": 3,
            "message": "expected ')' before 'return'",
            "raw": "test.c:3:5: error: expected ')' before 'return'"
        }
    ]
}

runtime_errors = {}
output_analysis = {}

print("\nGenerating explanation...")
print("-" * 70)

try:
    explanation = llm_service.generate_explanation(
        language="C",
        code=test_code,
        compile_errors=compile_errors,
        runtime_errors=runtime_errors,
        output_analysis=output_analysis
    )
    
    print("\n[OK] Explanation generated!")
    print("\nSummary:")
    print(f"  {explanation['summary']}")
    print("\nCause:")
    print(f"  {explanation['cause']}")
    print("\nFix:")
    print(f"  {explanation['fix']}")
    print("\nCorrected Code:")
    if explanation['corrected_code']:
        print("-" * 70)
        print(explanation['corrected_code'])
        print("-" * 70)
    else:
        print("  (No corrected code provided)")
    
    print("\n" + "=" * 70)
    print("[OK] Test completed successfully!")
    
except Exception as e:
    print(f"\n[X] Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


