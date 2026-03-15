"""
Debug script to see raw compiler output for C errors with line numbers.
"""
import sys
import subprocess
import tempfile
import os
from pathlib import Path

def debug_c_compiler_output():
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

    return 0
}"""
    with tempfile.TemporaryDirectory() as temp_dir:
        source_file = os.path.join(temp_dir, "program.c")
        with open(source_file, "w") as f:
            f.write(code)
            
        result = subprocess.run(
            ["gcc", "-o", os.path.join(temp_dir, "prog"), source_file, "-Wall"],
            capture_output=True,
            text=True
        )
        
        print("--- CODE ---")
        for i, line in enumerate(code.split('\n'), 1):
            print(f"{i}: {line}")
        print("--- END CODE ---")
        
        print("\n--- RAW STDERR ---")
        print(result.stderr)
        print("--- END RAW STDERR ---")

if __name__ == "__main__":
    debug_c_compiler_output()
