"""
Simple test script to verify the API is working.
Run this after starting the server to test the /analyze endpoint.
"""

import requests
import json

API_URL = "http://localhost:8000/api/analyze"

def test_c_compile_error():
    """Test C compilation error detection."""
    print("Testing C compilation error...")
    
    code = """
#include <stdio.h>
int main() {
    printf("Hello World\\n"
    return 0;
}
"""
    
    payload = {
        "language": "C",
        "code": code
    }
    
    try:
        response = requests.post(API_URL, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_java_runtime_error():
    """Test Java runtime error detection."""
    print("\nTesting Java runtime error...")
    
    code = """
public class Test {
    public static void main(String[] args) {
        int[] arr = new int[5];
        System.out.println(arr[10]);
    }
}
"""
    
    payload = {
        "language": "Java",
        "code": code
    }
    
    try:
        response = requests.post(API_URL, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_output_mismatch():
    """Test output comparison."""
    print("\nTesting output mismatch...")
    
    code = """
#include <stdio.h>
int main() {
    printf("Hello");
    return 0;
}
"""
    
    payload = {
        "language": "C",
        "code": code,
        "expected_output": "Hello World"
    }
    
    try:
        response = requests.post(API_URL, json=payload)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Output match: {result.get('output_analysis', {}).get('match')}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("API Test Suite")
    print("=" * 60)
    print("\nMake sure the server is running on http://localhost:8000")
    print()
    
    results = []
    results.append(("C Compile Error", test_c_compile_error()))
    results.append(("Java Runtime Error", test_java_runtime_error()))
    results.append(("Output Mismatch", test_output_mismatch()))
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{name}: {status}")


