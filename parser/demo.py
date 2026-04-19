"""
Demo script to showcase parser output.
Run this to see how test cases are parsed and structured.
"""

import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from parser import TestCaseParser


def main():
    """Run parser demo and display results."""
    
    csv_file = Path(__file__).parent.parent / "data" / "Source_TestCase.csv"
    
    print("=" * 80)
    print("🚀 PARSER DEMO - Test Case Structure Conversion")
    print("=" * 80)
    print(f"\n📁 Input File: {csv_file}")
    print(f"✅ File Exists: {csv_file.exists()}\n")
    
    # Parse test cases
    parser = TestCaseParser(str(csv_file))
    test_cases = parser.parse()
    errors = parser.get_errors()
    
    # Display summary
    print(f"\n📊 PARSING RESULTS")
    print("-" * 80)
    print(f"✅ Successfully Parsed: {len(test_cases)} test cases")
    if errors:
        print(f"⚠️  Errors Encountered: {len(errors)}")
        for error in errors:
            print(f"   - {error}")
    else:
        print(f"✅ No errors encountered")
    
    # Display each test case
    print(f"\n\n📋 PARSED TEST CASES (Structured Output)")
    print("=" * 80)
    
    for idx, case in enumerate(test_cases, start=1):
        print(f"\n[{idx}] Test Case ID: {case['id']}")
        print("-" * 80)
        print(f"   Title: {case['title']}")
        
        if case['precondition']:
            print(f"   Precondition: {case['precondition']}")
        
        print(f"\n   Steps ({len(case['steps'])} steps):")
        for step_idx, step in enumerate(case['steps'], start=1):
            print(f"      {step_idx}. {step}")
        
        if case['test_data']:
            print(f"\n   Test Data:")
            for key, value in case['test_data'].items():
                print(f"      • {key}: {value}")
        
        if case['expected_result']:
            print(f"\n   Expected Result: {case['expected_result']}")
    
    # Display JSON representation
    print(f"\n\n📄 JSON REPRESENTATION")
    print("=" * 80)
    print("\nThis is how the parser outputs structured data (first 2 cases shown):")
    print(json.dumps(test_cases[:2], indent=2))
    
    if len(test_cases) > 2:
        print(f"\n... and {len(test_cases) - 2} more test cases")
    
    # Save full output
    output_file = Path(__file__).parent.parent / "data" / "parsed_testcases.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(test_cases, f, indent=2)
    
    print(f"\n\n✅ Full JSON output saved to: {output_file}")
    print("\n" + "=" * 80)
    print("✨ Parser demo complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
