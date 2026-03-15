"""
Refined verification script for smart line mapping.
"""
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from services.compiler import CompilerService

def test_c_line_mapping():
    compiler = CompilerService()
    # Code with missing semicolon on line 4
    code = """#include <stdio.h>
int main() {
    int a = 10;
    int b = 20
    int sum;
    sum = a + b;
    printf("Sum is %d\\n", sum);
    return 0;
}
"""
    print("\n--- Testing C Line Mapping ---")
    print("Code snippet (lines 3-5):")
    lines = code.split('\n')
    print(f"3: {lines[2]}")
    print(f"4: {lines[3]}  <-- MISSING SEMICOLON HERE")
    print(f"5: {lines[4]}")
    
    result = compiler.compile_c(code)
    
    if not result["success"]:
        print(f"Compilation failed (expected). Status: {result['success']}")
        for i, err in enumerate(result["errors"]):
            print(f"Error {i+1}: Line {err['line']} | {err['message'][:150]}")
            if err['line'] == 4:
                print("✅ SUCCESS: Found error correctly mapped to line 4.")
                return True
        print("❌ FAILURE: No error mapped to line 4.")
    else:
        print("❌ FAILURE: Compilation succeeded unexpectedly.")
    return False

def test_java_line_mapping():
    compiler = CompilerService()
    # Java code with missing semicolon on line 3
    code = """public class Main {
    public static void main(String[] args) {
        int a = 10
        int b = 20;
        System.out.println(a + b);
    }
}
"""
    print("\n--- Testing Java Line Mapping ---")
    print("Code snippet (lines 2-4):")
    lines = code.split('\n')
    print(f"2: {lines[1]}")
    print(f"3: {lines[2]}  <-- MISSING SEMICOLON HERE")
    print(f"4: {lines[3]}")
    
    result = compiler.compile_java(code)
    
    if not result["success"]:
        print(f"Compilation failed (expected). Status: {result['success']}")
        for i, err in enumerate(result["errors"]):
            print(f"Error {i+1}: Line {err['line']} | {err['message'][:150]}")
            if err['line'] == 3:
                print("✅ SUCCESS: Found error correctly mapped to line 3.")
                return True
        print("❌ FAILURE: No error mapped to line 3.")
    else:
        print("❌ FAILURE: Compilation succeeded unexpectedly.")
    return False

if __name__ == "__main__":
    c_ok = test_c_line_mapping()
    j_ok = test_java_line_mapping()
    
    if c_ok and j_ok:
        print("\n🎉 ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n SOME TESTS FAILED.")
        sys.exit(1)
