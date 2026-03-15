
import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(r"c:\Users\L o V e\Desktop\akhil mainprj\new-one-main\backend")
sys.path.append(str(backend_dir))

from services.llm_service import LLMService

async def test_reproduction():
    llm = LLMService()
    if not llm.is_available():
        print("LLM Service not available. Check GEMINI_API_KEY.")
        return

    code = """#include <stdio.h>

int main() 
{
    int a = 10
    int b = 20;
    int sum;

    sum = a + b

    printf("The sum is %d", sum)

    if(sum > 20)
    {
        printf("Sum is greater than 20")
    else
    {
        printf("Sum is less than or equal to 20");
    }

    return 0"""

    compile_errors = {
        "success": False,
        "errors": [
            {"line": 5, "message": "expected ';' before 'int'", "raw": "test.c:5:10: error: expected ';' before 'int'"},
            {"line": 10, "message": "expected ';' before 'printf'", "raw": "test.c:10:5: error: expected ';' before 'printf'"},
            {"line": 12, "message": "expected ';' before 'if'", "raw": "test.c:12:5: error: expected ';' before 'if'"},
            {"line": 16, "message": "expected ';' before 'else'", "raw": "test.c:16:9: error: expected ';' before 'else'"},
            {"line": 21, "message": "expected ';' at end of input", "raw": "test.c:21:5: error: expected ';' at end of input"}
        ]
    }

    print("Generating explanation...")
    # We need to access the private _parse_response or see the generated text
    # Let's mock a bit or just use a helper to get the raw text
    
    # Actually, LLMService.generate_explanation doesn't return raw text.
    # I'll modify the script to print something from the llm object if I can, 
    # or just trust the logs if I could see them.
    # Wait, I can see the logs if I redirect them!
    
    # Run and capture output
    explanation = llm.generate_explanation(
        language="C",
        code=code,
        compile_errors=compile_errors,
        runtime_errors={"success": True},
        output_analysis={}
    )

    with open("explanation_output.txt", "w", encoding="utf-8") as f:
        f.write("\n--- RESULTS ---\n")
        f.write(f"Summary: {explanation.get('summary')}\n")
        
        cause = explanation.get('cause', '')
        f.write(f"Cause lines: {len(cause.splitlines())}\n")
        f.write("\nCAUSE CONTENT:\n")
        f.write(cause + "\n")
        
        if explanation.get('additional_errors'):
            f.write(f"\nAdditional errors: {len(explanation['additional_errors'])}\n")
    print("Done writing to explanation_output.txt")

if __name__ == "__main__":
    asyncio.run(test_reproduction())
