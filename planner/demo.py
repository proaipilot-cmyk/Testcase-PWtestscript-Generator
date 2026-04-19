"""
Planner Demo - Shows how parsed test cases are converted to canonical action schema
"""

import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from parser.parser import TestCaseParser
from planner.planner import plan_test_cases


def main():
    """Run planner demo and display results."""
    
    csv_file = Path(__file__).parent.parent / "data" / "Source_TestCase.csv"
    
    print("=" * 100)
    print("🚀 PLANNER DEMO - Test Case to Canonical Action Schema Conversion")
    print("=" * 100)
    print(f"\n📁 Input File: {csv_file}")
    print(f"✅ File Exists: {csv_file.exists()}\n")
    
    # Step 1: Parse test cases
    print("\n[STEP 1] PARSING TEST CASES")
    print("-" * 100)
    parser = TestCaseParser(str(csv_file))
    test_cases = parser.parse()
    errors = parser.get_errors()
    
    if errors:
        print(f"⚠️  Parsing Errors: {len(errors)}")
        for error in errors:
            print(f"   - {error}")
    else:
        print(f"✅ Successfully parsed {len(test_cases)} test cases with no errors")
    
    # Step 2: Plan test cases
    print("\n\n[STEP 2] PLANNING TEST CASES (Generating Canonical Actions)")
    print("-" * 100)
    planned_cases = plan_test_cases(test_cases)
    print(f"✅ Successfully planned {len(planned_cases)} test cases\n")
    
    # Display detailed output for first 2 cases
    for idx, case in enumerate(planned_cases[:2], start=1):
        print(f"\n{'=' * 100}")
        print(f"[CASE {idx}] {case['id']} - {case['title']}")
        print("=" * 100)
        
        if case['precondition']:
            print(f"📋 Precondition: {case['precondition']}")
        
        print(f"\n🎬 Actions ({len(case['actions'])} steps):\n")
        
        for action_idx, action in enumerate(case['actions'], start=1):
            action_type = action.get('type', 'unknown')
            print(f"   [{action_idx}] {action_type.upper()}")
            
            # Display action details
            for key, value in action.items():
                if key not in ['type', 'raw']:
                    print(f"        {key}: {value}")
            
            if action.get('raw'):
                print(f"        source: {action.get('raw')}")
            print()
        
        if case.get('expected_result'):
            print(f"✅ Expected Result: {case['expected_result']}\n")
    
    # Display JSON representation
    print("\n" + "=" * 100)
    print("📄 CANONICAL ACTION SCHEMA (JSON Format - First Case)")
    print("=" * 100)
    print(json.dumps(planned_cases[0], indent=2))
    
    if len(planned_cases) > 2:
        print(f"\n... and {len(planned_cases) - 2} more test cases processed")
    
    # Save full output
    output_file = Path(__file__).parent.parent / "data" / "planned_testcases.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(planned_cases, f, indent=2)
    
    print(f"\n✅ Full JSON output saved to: {output_file}")
    
    # Summary
    print("\n" + "=" * 100)
    print("📊 PLANNER SUMMARY")
    print("=" * 100)
    total_actions = sum(len(case.get('actions', [])) for case in planned_cases)
    print(f"Total test cases: {len(planned_cases)}")
    print(f"Total actions: {total_actions}")
    print(f"Average actions per case: {total_actions / len(planned_cases):.1f}")
    
    action_types = {}
    for case in planned_cases:
        for action in case.get('actions', []):
            atype = action.get('type', 'note')
            action_types[atype] = action_types.get(atype, 0) + 1
    
    print(f"\nAction Type Distribution:")
    for atype, count in sorted(action_types.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {atype}: {count}")
    
    print("\n" + "=" * 100)
    print("✨ Planner demo complete! Ready for Generator phase.")
    print("=" * 100)


if __name__ == "__main__":
    main()
