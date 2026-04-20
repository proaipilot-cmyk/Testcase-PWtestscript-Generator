import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from validator.validator import Validator

def main():
    base_dir = Path(__file__).parent.parent
    print("=" * 60)
    print("VALIDATOR DEMO")
    print("=" * 60)
    
    val = Validator(base_dir)
    report = val.validate_generated_framework()
    
    for res in report['results']:
        status = "PASS" if res['passed'] else "FAIL"
        print(f"[{status}] {res['name']}")
        for err in res['errors']:
            print(f"  ERR: {err}")
            
    print("=" * 60)
    print(f"SUMMARY: {report['summary']}")
    print("=" * 60)
    return 0 if report['total_errors'] == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
