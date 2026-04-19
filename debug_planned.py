"""Debug: Check what planned_cases contains"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from parser.parser import TestCaseParser
from planner.planner import Planner

csv_file = Path(__file__).parent.parent / "data" / "Source_TestCase.csv"

parser = TestCaseParser(str(csv_file))
test_cases = parser.parse()

planner = Planner()
planned_cases = planner.plan_cases(test_cases)

print("=" * 100)
print("FIRST 3 PLANNED CASES - CHECK TEST DATA EXTRACTION")
print("=" * 100)

for idx, case in enumerate(planned_cases[:3]):
    print(f"\n[{idx+1}] {case.get('id')} - {case.get('title')}")
    print(f"    Test Data: {case.get('test_data')}")
    print(f"    Expected: {case.get('expected_result')[:80]}")
    print(f"    Actions: {len(case.get('actions', []))} steps")
