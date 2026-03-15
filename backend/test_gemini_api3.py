"""
Test script to find correct Gemini API structure - Part 3.
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

try:
    import google.genai as genai
    
    client = genai.Client(api_key=api_key)
    
    # Check models attribute
    print("Checking client.models structure...")
    print(f"Type: {type(client.models)}")
    print(f"Attributes: {[x for x in dir(client.models) if not x.startswith('_')]}")
    
    # Try different methods
    test_prompt = "Say hello in one word"
    
    # Method 1: models.generate_content
    try:
        print("\nTrying: client.models.generate_content()...")
        response = client.models.generate_content(
            model='models/gemini-2.5-flash',
            contents=test_prompt
        )
        print("[OK] client.models.generate_content() works!")
        if hasattr(response, 'text'):
            print(f"Response: {response.text}")
        elif hasattr(response, 'candidates'):
            print(f"Response candidates: {response.candidates}")
        else:
            print(f"Response: {response}")
    except Exception as e:
        print(f"[X] Failed: {e}")
        print(f"   Error type: {type(e)}")
    
    # Method 2: Get model object first
    try:
        print("\nTrying: Get model object first...")
        # Check if models has a get method
        if hasattr(client.models, 'get'):
            model_obj = client.models.get('models/gemini-2.5-flash')
            print(f"Model object: {model_obj}")
            print(f"Model attributes: {[x for x in dir(model_obj) if not x.startswith('_')]}")
            
            if hasattr(model_obj, 'generate_content'):
                response = model_obj.generate_content(test_prompt)
                print("[OK] model.generate_content() works!")
                if hasattr(response, 'text'):
                    print(f"Response: {response.text}")
    except Exception as e:
        print(f"[X] Failed: {e}")
    
    # Method 3: Try old API as fallback
    print("\nTrying old API (google.generativeai)...")
    try:
        import google.generativeai as genai_old
        genai_old.configure(api_key=api_key)
        model = genai_old.GenerativeModel('gemini-pro')
        response = model.generate_content(test_prompt)
        print("[OK] Old API works!")
        if hasattr(response, 'text'):
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"[X] Old API failed: {e}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()


