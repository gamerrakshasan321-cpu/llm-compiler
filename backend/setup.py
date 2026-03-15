"""
Setup script to help configure the backend environment.
Run this script to set up the .env file interactively.
"""

import os
import sys

def setup_env():
    """Interactive setup for environment variables."""
    print("=" * 60)
    print("AI Compiler Debugging Assistant - Backend Setup")
    print("=" * 60)
    print()
    
    # Check if .env already exists
    if os.path.exists(".env"):
        response = input(".env file already exists. Overwrite? (y/n): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            return
    
    # Get Gemini API key
    print("Enter your Google Gemini API key.")
    print("(You can get one from: https://makersuite.google.com/app/apikey)")
    api_key = input("GEMINI_API_KEY: ").strip()
    
    if not api_key:
        print("Error: API key cannot be empty!")
        sys.exit(1)
    
    # Get port (optional)
    port = input("Port (default: 8000): ").strip()
    if not port:
        port = "8000"
    
    # Get environment (optional)
    env = input("Environment (default: development): ").strip()
    if not env:
        env = "development"
    
    # Write .env file
    env_content = f"""GEMINI_API_KEY={api_key}
PORT={port}
ENVIRONMENT={env}
"""
    
    try:
        with open(".env", "w") as f:
            f.write(env_content)
        print("\n✓ .env file created successfully!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run the server: python main.py")
    except Exception as e:
        print(f"\n✗ Error creating .env file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup_env()


