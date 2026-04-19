"""
Generator Demo - Converts planned test cases to POM framework
"""
import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from parser.parser import TestCaseParser
from planner.planner import Planner
from generator.generator import Generator


def main():
    """Run generator demo."""
    
    csv_file = Path(__file__).parent.parent / "data" / "Source_TestCase.csv"
    
    print("=" * 100)
    print("🚀 GENERATOR DEMO - Canonical Actions to Playwright POM Framework")
    print("=" * 100)
    
    # Step 1: Parse
    print("\n[STEP 1] PARSING TEST CASES")
    print("-" * 100)
    parser = TestCaseParser(str(csv_file))
    test_cases = parser.parse()
    print(f"✅ Parsed {len(test_cases)} test cases\n")
    
    # Step 2: Plan
    print("[STEP 2] PLANNING TEST CASES")
    print("-" * 100)
    planner = Planner()
    planned_cases = planner.plan_cases(test_cases)
    print(f"✅ Planned {len(planned_cases)} test cases\n")
    
    # Step 3: Generate
    print("[STEP 3] GENERATING POM FRAMEWORK")
    print("-" * 100)
    generator = Generator()
    result = generator.generate(planned_cases)
    print(f"✅ Generated framework:\n")
    print(json.dumps(result['summary'], indent=2))
    
    # Display file structure
    print("\n📁 Generated Files:")
    print("-" * 100)
    for category, files in result.items():
        if category not in ('timestamp', 'summary'):
            for name, path_str in files.items():
                print(f"  ✓ {path_str}")
    
    print(f"\n✅ Framework ready in: {Path('.').absolute()}")
    print("=" * 100)


if __name__ == "__main__":
    main()