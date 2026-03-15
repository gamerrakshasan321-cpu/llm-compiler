"""
Test script to find correct Gemini API structure.
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
    print("Using google.genai (new API)")
    
    client = genai.Client(api_key=api_key)
    
    # List available models
    print("\nListing available models...")
    try:
        models = client.models.list()
        print("Available models:")
        for model in models:
            print(f"  - {model.name}")
            if hasattr(model, 'supported_generation_methods'):
                print(f"    Methods: {model.supported_generation_methods}")
    except Exception as e:
        print(f"Could not list models: {e}")
    
    # Try to find the correct way to generate content
    print("\nTrying different API methods...")
    
    # Method: Check client structure
    print("\nClient attributes:")
    print(f"  dir(client): {[x for x in dir(client) if not x.startswith('_')]}")
    
    # Try generate_content directly on client
    try:
        print("\nTrying: client.generate_content()...")
        response = client.generate_content(
            model='gemini-1.5-flash',
            contents="Say hello"
        )
        print("[OK] client.generate_content() works!")
        print(f"Response: {response}")
    except Exception as e:
        print(f"[X] client.generate_content() failed: {e}")
    
    # Try with different model names
    model_names = ['gemini-1.5-flash', 'gemini-1.5-flash-002', 'gemini-pro', 'models/gemini-1.5-flash']
    for model_name in model_names:
        try:
            print(f"\nTrying model: {model_name}")
            response = client.generate_content(
                model=model_name,
                contents="Say hello"
            )
            print(f"[OK] Model {model_name} works!")
            if hasattr(response, 'text'):
                print(f"Response text: {response.text[:100]}")
            break
        except Exception as e:
            print(f"[X] Model {model_name} failed: {e}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()


