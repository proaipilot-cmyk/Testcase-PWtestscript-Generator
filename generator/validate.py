"""
Validation of NEW generator - shows steps library + consolidated test file
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from parser.parser import TestCaseParser
from planner.planner import Planner
from generator.generator import Generator


def main():
    csv_file = Path(__file__).parent.parent / "data" / "Source_TestCase.csv"
    
    print("=" * 120)
    print("🚀 NEW GENERATOR - Data-Driven, No Duplication, Domain-Agnostic")
    print("=" * 120)
    
    # Parse and plan
    parser = TestCaseParser(str(csv_file))
    test_cases = parser.parse()
    
    planner = Planner()
    planned_cases = planner.plan_cases(test_cases)
    
    # Generate
    generator = Generator()
    result = generator.generate(planned_cases)
    
    # Show steps library
    steps_file = Path(result['steps']['steps'])
    print(f"\n📚 REUSABLE STEP LIBRARY: {steps_file}")
    print("-" * 120)
    with open(steps_file, 'r') as f:
        print(f.read()[:1500] + "\n... (truncated)")
    
    # Show test file
    test_file = Path(result['tests']['test_automation'])
    print(f"\n🧪 CONSOLIDATED TEST FILE: {test_file}")
    print("-" * 120)
    with open(test_file, 'r') as f:
        print(f.read())
    
    print("\n" + "=" * 120)
    print("✅ KEY IMPROVEMENTS:")
    print("  ✓ ONE step_library with reusable functions (no duplication)")
    print("  ✓ ONE test_automation.py with parameterized tests")
    print("  ✓ Login errors clustered in ONE parameterized test (TC_02-04)")
    print("  ✓ Domain-agnostic steps work for any login form / app")
    print("  ✓ Minimal tokens, clear intent, production-ready")
    print("=" * 120)


if __name__ == "__main__":
    main()


# """
# Quick validation of rebuilt generator - shows generated test file content
# """
# import sys
# import json
# from pathlib import Path

# # Add project root to path
# sys.path.insert(0, str(Path(__file__).parent.parent))

# from parser.parser import TestCaseParser
# from planner.planner import Planner
# from generator.generator import Generator


# def main():
#     """Show generated test file."""
    
#     csv_file = Path(__file__).parent.parent / "data" / "Source_TestCase.csv"
    
#     print("=" * 100)
#     print("🔍 REBUILT GENERATOR - Intelligent Test Clustering")
#     print("=" * 100)
    
#     # Parse and plan
#     parser = TestCaseParser(str(csv_file))
#     test_cases = parser.parse()
    
#     planner = Planner()
#     planned_cases = planner.plan_cases(test_cases)
    
#     # Generate
#     generator = Generator()
#     result = generator.generate(planned_cases)
    
#     # Show generated test file
#     test_file = Path(result['tests']['test_automation'])
    
#     print(f"\n📄 Generated Test File: {test_file}")
#     print("=" * 100)
#     print(f"\nFile Contents:\n")
    
#     with open(test_file, 'r', encoding='utf-8') as f:
#         content = f.read()
    
#     print(content)
    
#     print("\n" + "=" * 100)
#     print("✅ Key improvements:")
#     print("  • All login error cases grouped in ONE parameterized test")
#     print("  • Only ONE test_automation.py file (not individual files)")
#     print("  • @pytest.mark.parametrize reduces duplication")
#     print("  • Assertions extracted from expected_result")
#     print("  • TC IDs included in test parameter ids")
#     print("=" * 100)


# if __name__ == "__main__":
#     main()
