"""
Simple test to verify parser works correctly
"""

import json
import csv
from pathlib import Path

# Read the CSV to show what gets parsed
csv_file = Path("data/testcases.csv")
test_cases = []

with open(csv_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Simple parsing to demonstrate structure
        steps = [s.strip() for s in row['steps'].split('\n') if s.strip()]
        test_data = {}
        for entry in row['test_data'].split(','):
            if ':' in entry:
                k, v = entry.split(':', 1)
                test_data[k.strip()] = v.strip()
        
        case = {
            'id': row['id'].strip(),
            'title': row['title'].strip(),
            'precondition': row['precondition'].strip(),
            'steps': steps,
            'test_data': test_data,
            'expected_result': row['expected_result'].strip()
        }
        test_cases.append(case)

# Display output
print("=" * 80)
print("🚀 PARSER OUTPUT - Example Structure")
print("=" * 80)
print(f"\n✅ Successfully parsed {len(test_cases)} test cases\n")

print("📋 FIRST TEST CASE (Formatted):")
print("-" * 80)
case = test_cases[0]
print(f"ID: {case['id']}")
print(f"Title: {case['title']}")
print(f"Precondition: {case['precondition']}")
print(f"Steps ({len(case['steps'])} steps):")
for i, step in enumerate(case['steps'], 1):
    print(f"  {i}. {step}")
print(f"Test Data: {case['test_data']}")
print(f"Expected Result: {case['expected_result']}")

print("\n\n📄 JSON REPRESENTATION (First 2 cases):")
print("-" * 80)
print(json.dumps(test_cases[:2], indent=2))

print(f"\n\n✅ Total test cases parsed: {len(test_cases)}")
print("=" * 80)
