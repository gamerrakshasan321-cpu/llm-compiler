"""
Helper script to update GEMINI_API_KEY in .env file.
This ensures the API key is saved correctly and can be verified.
"""

import os
import sys
from pathlib import Path

def update_api_key(new_key: str):
    """Update the API key in .env file."""
    backend_dir = Path(__file__).parent
    env_file = backend_dir / ".env"
    
    print("=" * 70)
    print("GEMINI API KEY UPDATER")
    print("=" * 70)
    print()
    
    # Read existing .env file
    env_vars = {}
    if env_file.exists():
        print(f"Reading existing .env file: {env_file}")
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
            print(f"[OK] Found {len(env_vars)} existing variables")
        except Exception as e:
            print(f"[!] Error reading .env file: {e}")
            return False
    else:
        print(f"[INFO] .env file not found, will create new one")
    
    # Update the API key
    old_key = env_vars.get('GEMINI_API_KEY', '')
    env_vars['GEMINI_API_KEY'] = new_key.strip()
    
    # Show what's being updated
    print()
    print("Updating GEMINI_API_KEY:")
    if old_key:
        print(f"  Old: {old_key[:10]}...{old_key[-5:] if len(old_key) > 15 else '***'}")
    else:
        print("  Old: (not set)")
    print(f"  New: {new_key[:10]}...{new_key[-5:] if len(new_key) > 15 else '***'}")
    print()
    
    # Write back to .env file
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            # Write GEMINI_API_KEY first
            f.write(f"GEMINI_API_KEY={new_key.strip()}\n")
            # Write other variables (excluding GEMINI_API_KEY which we already wrote)
            for key, value in env_vars.items():
                if key != 'GEMINI_API_KEY':
                    f.write(f"{key}={value}\n")
        
        print(f"[OK] Successfully updated .env file: {env_file}")
        print()
        
        # Verify it was written correctly
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if f"GEMINI_API_KEY={new_key.strip()}" in content:
                print("[OK] Verification: API key correctly saved in .env file")
            else:
                print("[!] WARNING: Could not verify API key was saved correctly")
        
        print()
        print("=" * 70)
        print("IMPORTANT: Restart your backend server for changes to take effect!")
        print("=" * 70)
        print()
        print("Next steps:")
        print("1. Stop your backend server (Ctrl+C)")
        print("2. Start it again: python main.py")
        print("3. Run: python check_api_key.py (to verify)")
        print()
        
        return True
        
    except Exception as e:
        print(f"[X] Error writing .env file: {e}")
        return False

def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python update_api_key.py <your_api_key>")
        print()
        print("Example:")
        print("  python update_api_key.py AIzaSyDAvXrd-hIRgTDVHcAGT6UnFJA2pSHTLjA")
        print()
        sys.exit(1)
    
    new_key = sys.argv[1]
    
    if not new_key.strip():
        print("[X] Error: API key cannot be empty")
        sys.exit(1)
    
    if not new_key.startswith('AIza'):
        print("[!] Warning: API key doesn't start with 'AIza'")
        print("   This might not be a valid Gemini API key")
        response = input("   Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    success = update_api_key(new_key)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

