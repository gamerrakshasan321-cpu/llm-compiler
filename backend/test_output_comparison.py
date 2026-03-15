"""
Test script to verify output comparison logic.
"""

from services.analyzer import CodeAnalyzer

# Test cases
test_cases = [
    {
        "name": "Simple numeric match",
        "actual": "3",
        "expected": "3",
        "should_match": True
    },
    {
        "name": "Numeric with newline",
        "actual": "3\n",
        "expected": "3",
        "should_match": True
    },
    {
        "name": "Numeric with spaces",
        "actual": "  3  ",
        "expected": "3",
        "should_match": True
    },
    {
        "name": "Numeric mismatch",
        "actual": "3",
        "expected": "4",
        "should_match": False
    },
    {
        "name": "Multiline match",
        "actual": "Hello\nWorld",
        "expected": "Hello\nWorld",
        "should_match": True
    },
]

analyzer = CodeAnalyzer()

print("Testing Output Comparison Logic")
print("=" * 70)

for test in test_cases:
    result = analyzer._analyze_output(test["actual"], test["expected"])
    match = result["match"]
    expected_match = test["should_match"]
    
    status = "[PASS]" if match == expected_match else "[FAIL]"
    
    print(f"\n{status} - {test['name']}")
    print(f"  Actual:   '{test['actual']}'")
    print(f"  Expected: '{test['expected']}'")
    print(f"  Match:    {match} (expected {expected_match})")
    print(f"  Normalized actual:   '{result['actual']}'")
    print(f"  Normalized expected: '{result['expected']}'")
    
    if match != expected_match:
        print(f"  [!] MISMATCH DETECTED!")

print("\n" + "=" * 70)

