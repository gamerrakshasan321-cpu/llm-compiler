"""
Diagnostic script to check GEMINI_API_KEY configuration.
Run this script to verify your API key is set up correctly.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def check_env_file():
    """Check if .env file exists and is readable."""
    backend_dir = Path(__file__).parent
    env_file = backend_dir / ".env"
    
    print("=" * 70)
    print("GEMINI API KEY DIAGNOSTIC TOOL")
    print("=" * 70)
    print()
    
    print(f"Checking for .env file in: {backend_dir}")
    print()
    
    if not env_file.exists():
        print("[X] .env file NOT FOUND!")
        print()
        print("SOLUTION:")
        print("1. Create a file named '.env' in the backend directory")
        print(f"   Location: {env_file}")
        print()
        print("2. Add the following line to the .env file:")
        print("   GEMINI_API_KEY=your_api_key_here")
        print()
        print("3. Replace 'your_api_key_here' with your actual Gemini API key")
        print("   Get your API key from: https://makersuite.google.com/app/apikey")
        print()
        return False, None
    
    print("[OK] .env file found!")
    print()
    
    # Read the file to check its contents
    try:
        with open(env_file, 'r') as f:
            content = f.read()
            lines = content.strip().split('\n')
            
        print("Contents of .env file:")
        print("-" * 70)
        for i, line in enumerate(lines, 1):
            # Mask the API key for security
            if 'GEMINI_API_KEY' in line.upper():
                parts = line.split('=', 1)
                if len(parts) == 2:
                    masked_key = parts[1][:10] + "..." + parts[1][-5:] if len(parts[1]) > 15 else "***"
                    print(f"  Line {i}: {parts[0]}={masked_key}")
                else:
                    print(f"  Line {i}: {line}")
            else:
                print(f"  Line {i}: {line}")
        print("-" * 70)
        print()
    except Exception as e:
        print(f"[!] Warning: Could not read .env file: {e}")
        print()
        return False, None
    
    return True, env_file

def check_api_key_loaded():
    """Check if API key is loaded from environment."""
    # Load .env file explicitly
    backend_dir = Path(__file__).parent
    env_file = backend_dir / ".env"
    
    # First, clear any existing GEMINI_API_KEY from environment to force reload
    if "GEMINI_API_KEY" in os.environ:
        del os.environ["GEMINI_API_KEY"]
        print("[INFO] Cleared existing GEMINI_API_KEY from environment to force reload")
        print()
    
    # Read the .env file directly to show what's actually in it
    if env_file.exists():
        print(f"Reading .env file from: {env_file}")
        print()
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                env_content = f.read()
                # Find GEMINI_API_KEY line
                for line in env_content.split('\n'):
                    if line.strip().startswith('GEMINI_API_KEY'):
                        # Show the line (masked)
                        parts = line.split('=', 1)
                        if len(parts) == 2:
                            key_value = parts[1].strip()
                            masked = key_value[:10] + "..." + key_value[-5:] if len(key_value) > 15 else "***"
                            print(f"Found in .env file: GEMINI_API_KEY={masked}")
                            print(f"  Full key length: {len(key_value)} characters")
                            print()
        except Exception as e:
            print(f"[!] Could not read .env file: {e}")
            print()
        
        # Load from specific path with override
        load_dotenv(dotenv_path=env_file, override=True)
    else:
        print(f"[!] .env file not found at: {env_file}")
        print("   Trying default location...")
        print()
        # Try default location
        load_dotenv(override=True)
    
    api_key = os.getenv("GEMINI_API_KEY")
    
    print("Checking if API key is loaded from environment...")
    print()
    
    if not api_key:
        print("[X] GEMINI_API_KEY is NOT loaded from environment!")
        print()
        print("POSSIBLE ISSUES:")
        print("1. .env file doesn't contain GEMINI_API_KEY")
        print("2. .env file has incorrect format")
        print("3. .env file is in wrong location")
        print()
        print("CORRECT FORMAT:")
        print("  GEMINI_API_KEY=AIzaSy...your_key_here")
        print()
        print("COMMON MISTAKES:")
        print("  [X] GEMINI_API_KEY = value (spaces around =)")
        print("  [X] GEMINI_API_KEY='value' (quotes)")
        print("  [X] GEMINI_API_KEY=\"value\" (quotes)")
        print("  [OK] GEMINI_API_KEY=value (correct)")
        print()
        return False, None
    
    # Check key format
    if not api_key.startswith('AIza'):
        print("[!] Warning: API key doesn't start with 'AIza'")
        print("   This might not be a valid Gemini API key format")
        print()
    
    print(f"[OK] API key loaded successfully!")
    print(f"   Key length: {len(api_key)} characters")
    print(f"   Key preview: {api_key[:10]}...{api_key[-5:]}")
    print()
    
    # Verify it matches what's in the file
    if env_file.exists():
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip().startswith('GEMINI_API_KEY'):
                        file_key = line.split('=', 1)[1].strip() if '=' in line else ""
                        if file_key == api_key:
                            print("[OK] Loaded API key matches .env file content")
                        else:
                            print("[!] WARNING: Loaded API key does NOT match .env file!")
                            print(f"   File has: {file_key[:10]}...{file_key[-5:]}")
                            print(f"   Loaded:   {api_key[:10]}...{api_key[-5:]}")
                            print("   This might mean:")
                            print("   - Environment variable is set elsewhere (system/user env)")
                            print("   - Another .env file is being loaded")
                            print("   - .env file wasn't saved properly")
                        print()
                        break
        except Exception:
            pass
    
    return True, api_key

def test_api_key(api_key):
    """Test the API key by trying to initialize the LLM service."""
    print("Testing API key with Gemini API...")
    print()
    
    try:
        # Try importing the packages
        try:
            import google.genai as genai_new
            USE_NEW_API = True
            genai = genai_new
            print("[OK] Using google.genai (new API)")
        except ImportError:
            try:
                import google.generativeai as genai
                USE_NEW_API = False
                print("[OK] Using google.generativeai (old API)")
            except ImportError:
                print("[X] Neither google.genai nor google.generativeai is installed!")
                print()
                print("SOLUTION:")
                print("  pip install google-genai google-generativeai")
                print()
                return False
        
        # Try to configure with the API key
        try:
            if USE_NEW_API:
                try:
                    client = genai.Client(api_key=api_key)
                    print("[OK] Successfully initialized Gemini client (new API)")
                    return True
                except Exception as e:
                    print(f"[!] New API failed: {e}")
                    print("   Trying old API...")
                    USE_NEW_API = False
            
            if not USE_NEW_API:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-pro')
                print("[OK] Successfully configured Gemini API (old API)")
                return True
                
        except Exception as e:
            error_msg = str(e).lower()
            print(f"[X] Failed to initialize Gemini API!")
            print(f"   Error: {e}")
            print()
            
            if "api key" in error_msg or "invalid" in error_msg or "401" in error_msg or "403" in error_msg:
                print("DIAGNOSIS: Invalid or unauthorized API key")
                print()
                print("SOLUTIONS:")
                print("1. Verify your API key is correct")
                print("   - Check: https://makersuite.google.com/app/apikey")
                print("2. Make sure the API key hasn't expired")
                print("3. Ensure API key has proper permissions")
                print("4. Remove any quotes or spaces from the API key in .env file")
            elif "quota" in error_msg or "429" in error_msg:
                print("DIAGNOSIS: API quota exceeded")
                print()
                print("SOLUTION: Check your API usage limits")
            else:
                print("DIAGNOSIS: Unknown error")
                print()
                print("SOLUTION: Check the error message above and verify:")
                print("  - API key is correct")
                print("  - Internet connection is working")
                print("  - Gemini API service is available")
            
            return False
            
    except Exception as e:
        print(f"[X] Unexpected error: {e}")
        return False

def main():
    """Main diagnostic function."""
    # Check .env file
    env_exists, env_file = check_env_file()
    if not env_exists:
        print("\n" + "=" * 70)
        print("SUMMARY: .env file not found. Please create it first.")
        print("=" * 70)
        sys.exit(1)
    
    # Check if API key is loaded
    key_loaded, api_key = check_api_key_loaded()
    if not key_loaded:
        print("\n" + "=" * 70)
        print("SUMMARY: API key not loaded. Please check .env file format.")
        print("=" * 70)
        sys.exit(1)
    
    # Test the API key
    api_works = test_api_key(api_key)
    
    print()
    print("=" * 70)
    if api_works:
        print("[OK] ALL CHECKS PASSED!")
        print("   Your Gemini API key is configured correctly.")
        print("   The LLM service should work now.")
    else:
        print("[X] API KEY TEST FAILED")
        print("   Please follow the solutions above to fix the issue.")
    print("=" * 70)
    print()
    
    if not api_works:
        sys.exit(1)

if __name__ == "__main__":
    main()

