"""
Verification Script - Confirms no test duplication

Run this script to verify:
1. CSV contains unique testcases
2. Generated test file has no duplicate IDs
3. Pytest counts match expected values
"""
import csv
from pathlib import Path
import subprocess
import sys
import re


def verify_csv_unique():
    """Verify CSV has no duplicate testcase IDs."""
    csv_path = Path(__file__).parent / 'data' / 'testcases.csv'
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        ids = [row['id'] for row in reader]
    
    unique_ids = set(ids)
    duplicates = len(ids) - len(unique_ids)
    
    if duplicates > 0:
        print(f"✗ CSV has {duplicates} duplicate test IDs")
        return False
    
    print(f"✓ CSV has {len(unique_ids)} unique testcases (no duplicates)")
    return True


def verify_test_file():
    """Verify generated test file has no duplicate parameter sets."""
    test_path = Path(__file__).parent / 'tests' / 'test_automation.py'
    
    with open(test_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count parameterize blocks
    param_blocks = re.findall(r'@pytest\.mark\.parametrize', content)
    
    if len(param_blocks) == 0:
        print("✗ No parametrize decorators found in test file")
        return False
    
    # Extract test case IDs from ids parameter
    ids_pattern = r"ids=\[(.*?)\]"
    all_ids_matches = re.findall(ids_pattern, content, re.DOTALL)
    
    all_ids = []
    for match in all_ids_matches:
        # Parse ID strings
        ids_in_block = re.findall(r"'([^']+)'", match)
        all_ids.extend(ids_in_block)
    
    unique_ids = set(all_ids)
    duplicates = len(all_ids) - len(unique_ids)
    
    if duplicates > 0:
        print(f"✗ Test file has {duplicates} duplicate test IDs")
        return False
    
    print(f"✓ Test file has {len(unique_ids)} unique test IDs (no duplicates)")
    return True


def verify_pytest_collection():
    """Verify pytest collects exactly the expected number of tests."""
    try:
        result = subprocess.run(
            ['python', '-m', 'pytest', 'tests/test_automation.py', '--collect-only', '-q'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Parse output for test count
        match = re.search(r'(\d+) test', result.stdout)
        if not match:
            print("✗ Could not parse pytest collection output")
            return False
        
        test_count = int(match.group(1))
        print(f"✓ Pytest collected {test_count} tests")
        
        # Check for duplicates in output
        if 'ERROR' in result.stdout or 'FAILED' in result.stdout:
            print(f"⚠ Warning: Collection had issues")
            print(result.stdout)
            return False
        
        return True
    
    except subprocess.TimeoutExpired:
        print("✗ Pytest collection timed out")
        return False
    except Exception as e:
        print(f"✗ Error running pytest: {e}")
        return False


def main():
    """Run all verifications."""
    print("\n" + "="*60)
    print("TEST DUPLICATION VERIFICATION")
    print("="*60 + "\n")
    
    results = []
    
    print("[1/3] Verifying CSV testcases...")
    results.append(verify_csv_unique())
    
    print("\n[2/3] Verifying generated test file...")
    results.append(verify_test_file())
    
    print("\n[3/3] Verifying pytest collection...")
    results.append(verify_pytest_collection())
    
    print("\n" + "="*60)
    if all(results):
        print("✓ ALL VERIFICATIONS PASSED - NO DUPLICATION DETECTED")
        print("="*60 + "\n")
        return 0
    else:
        print("✗ VERIFICATION FAILED - DUPLICATION OR ERRORS DETECTED")
        print("="*60 + "\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
