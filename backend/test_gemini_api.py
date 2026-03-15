"""
Test script to verify Gemini API is working correctly.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env
backend_dir = Path(__file__).parent
env_file = backend_dir / ".env"
if env_file.exists():
    load_dotenv(dotenv_path=env_file, override=True)
else:
    load_dotenv(override=True)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("[X] GEMINI_API_KEY not found!")
    exit(1)

print("Testing Gemini API...")
print()

# Try new API first
try:
    import google.genai as genai
    print("[OK] Using google.genai (new API)")
    
    # Initialize client
    client = genai.Client(api_key=api_key)
    print("[OK] Client initialized")
    
    # Test with a simple prompt
    test_prompt = """You are a C programming tutor. Analyze this code:

```c
#include <stdio.h>
int main() {
    printf("Hello"
    return 0;
}
```

There's a syntax error. Provide a JSON response:
{
  "summary": "Brief explanation",
  "cause": "Detailed cause",
  "fix": "How to fix",
  "corrected_code": "The corrected code"
}
"""
    
    print("Sending test request to Gemini...")
    print()
    
    # Try different API structures
    try:
        # Method 1: Direct generate_content
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=test_prompt
        )
        print("[OK] Method 1 worked: client.models.generate_content")
    except Exception as e1:
        print(f"[!] Method 1 failed: {e1}")
        try:
            # Method 2: Get model first
            model = client.models.get('gemini-1.5-flash')
            response = model.generate_content(test_prompt)
            print("[OK] Method 2 worked: client.models.get().generate_content")
        except Exception as e2:
            print(f"[!] Method 2 failed: {e2}")
            try:
                # Method 3: Direct model access
                response = genai.GenerativeModel('gemini-1.5-flash').generate_content(test_prompt)
                print("[OK] Method 3 worked: GenerativeModel.generate_content")
            except Exception as e3:
                print(f"[X] All methods failed!")
                print(f"   Method 3 error: {e3}")
                exit(1)
    
    # Extract response
    print()
    print("Response received:")
    print("-" * 70)
    
    if hasattr(response, 'text'):
        response_text = response.text
        print(response_text)
    elif hasattr(response, 'candidates') and len(response.candidates) > 0:
        candidate = response.candidates[0]
        if hasattr(candidate, 'content'):
            if hasattr(candidate.content, 'parts'):
                response_text = ''.join([part.text for part in candidate.content.parts if hasattr(part, 'text')])
            elif hasattr(candidate.content, 'text'):
                response_text = candidate.content.text
            else:
                response_text = str(candidate.content)
        else:
            response_text = str(candidate)
        print(response_text)
    else:
        print("Response structure:")
        print(response)
        response_text = str(response)
    
    print("-" * 70)
    print()
    print("[OK] Gemini API is working correctly!")
    
except ImportError:
    print("[!] google.genai not available, trying old API...")
    try:
        import google.generativeai as genai_old
        genai_old.configure(api_key=api_key)
        model = genai_old.GenerativeModel('gemini-pro')
        
        test_prompt = """You are a C programming tutor. Analyze this code:

```c
#include <stdio.h>
int main() {
    printf("Hello"
    return 0;
}
```

There's a syntax error. Provide a JSON response:
{
  "summary": "Brief explanation",
  "cause": "Detailed cause",
  "fix": "How to fix",
  "corrected_code": "The corrected code"
}
"""
        
        print("Sending test request to Gemini (old API)...")
        response = model.generate_content(test_prompt)
        
        print()
        print("Response received:")
        print("-" * 70)
        if hasattr(response, 'text'):
            print(response.text)
        else:
            print(response)
        print("-" * 70)
        print()
        print("[OK] Gemini API (old) is working correctly!")
        
    except Exception as e:
        print(f"[X] Old API also failed: {e}")
        exit(1)


