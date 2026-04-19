"""
Validator Demo - Comprehensive validation of generated POM framework
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from validator.validator import Validator


def main():
    """Run validation on generated framework."""
    
    base_dir = Path(__file__).parent.parent
    
    print("=" * 120)
    print("✅ VALIDATOR - Comprehensive Framework Quality Checks")
    print("=" * 120)
    
    # Run validation
    validator = Validator(base_dir)
    report = validator.validate_generated_framework()
    
    # Display results
    print(f"\n📊 VALIDATION REPORT")
    print("-" * 120)
    print(f"Total Checks: {report['total_checks']}")
    print(f"Passed: {report['passed']} ✅")
    print(f"Failed: {report['failed']} ❌")
    print(f"Errors: {report['total_errors']}")
    print(f"Warnings: {report['total_warnings']}")
    
    # Display detailed results
    print(f"\n\n📋 DETAILED RESULTS")
    print("-" * 120)
    
    for result in report['results']:
        status = "✅ PASS" if result['passed'] else "❌ FAIL"
        print(f"\n[{status}] {result['name']}")
        
        if result['errors']:
            print(f"   Errors ({len(result['errors'])}):")
            for error in result['errors']:
                print(f"      ❌ {error}")
        
        if result['warnings']:
            print(f"   Warnings ({len(result['warnings'])}):")
            for warning in result['warnings']:
                print(f"      ⚠️  {warning}")
    
    # Summary
    print(f"\n\n" + "=" * 120)
    print(f"SUMMARY: {report['summary']}")
    print("=" * 120)
    
    if report['total_errors'] == 0:
        print("\n✅ Framework is production-ready!")
        print("\nNext steps:")
        print("  1. Run tests: pytest tests/test_automation.py -v")
        print("  2. Generate report: pytest tests/test_automation.py --html=report.html")
        print("  3. Check coverage: pytest --cov=steps --cov=pages tests/")
    else:
        print(f"\n❌ Fix {report['total_errors']} error(s) before running tests")
    
    return 0 if report['total_errors'] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
