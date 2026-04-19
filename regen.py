#!/usr/bin/env python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from parser.parser import TestCaseParser
from planner.planner import Planner
from generator.generator import Generator

csv_file = Path(__file__).parent / "data" / "Source_TestCase.csv"

parser = TestCaseParser(str(csv_file))
test_cases = parser.parse()
print(f"Parsed: {len(test_cases)} cases")

planner = Planner()
planned_cases = planner.plan_cases(test_cases)
print(f"Planned: {len(planned_cases)} cases")

generator = Generator()
result = generator.generate(planned_cases)
print(f"Generated tests at: {result['tests']['test_automation']}")

# Check the test file
test_file = Path(__file__).parent / 'tests' / 'test_automation.py'
with open(test_file) as f:
    content = f.read()

# Count test functions
login_success_count = content.count('def test_login_success')
login_errors_count = content.count('def test_login_error_scenarios')
skipped_count = content.count('# NOTE:')

print(f"\nGenerated Test File:")
print(f"  test_login_success: {login_success_count}")
print(f"  test_login_error_scenarios: {login_errors_count}")
print(f"  Skipped sections: {skipped_count}")

# Show parameter count
if '@pytest.mark.parametrize' in content:
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if '@pytest.mark.parametrize' in line:
            # Count parameter lines
            j = i + 1
            param_count = 0
            while j < len(lines) and '], ids=' not in lines[j]:
                if lines[j].strip().startswith('('):
                    param_count += 1
                j += 1
            print(f"  login_errors parameters: {param_count}")
            break

print("\n✓ Tests regenerated successfully!")
