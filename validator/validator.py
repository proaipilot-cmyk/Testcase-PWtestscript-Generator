"""
Validator Module - Comprehensive syntax, structure, and quality validation
"""

import ast
import json
import sys
import io
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional


class ValidationResult:
    def __init__(self, name: str):
        self.name = name
        self.passed = True
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def add_error(self, msg: str) -> None:
        self.passed = False
        self.errors.append(msg)
    
    def add_warning(self, msg: str) -> None:
        self.warnings.append(msg)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'passed': self.passed,
            'errors': self.errors,
            'warnings': self.warnings,
            'error_count': len(self.errors),
            'warning_count': len(self.warnings)
        }


class Validator:
    """Main validator orchestrator - sanitized for Windows/Any app."""
    
    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or Path('.')
        self.results: List[ValidationResult] = []
    
    def _validate_syntax(self, file_path: Path) -> ValidationResult:
        res = ValidationResult(f"Syntax: {file_path.name}")
        if not file_path.exists():
            res.add_error(f"File missing: {file_path}")
            return res
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                ast.parse(f.read())
            res.add_warning("Syntax OK")
        except SyntaxError as e:
            res.add_error(f"Syntax error at line {e.lineno}: {e.msg}")
        except Exception as e:
            res.add_error(f"Parse error: {str(e)}")
        return res

    def validate_generated_framework(self) -> Dict[str, Any]:
        test_file = self.base_dir / 'tests' / 'test_automation.py'
        conftest_file = self.base_dir / 'tests' / 'conftest.py'
        
        self.results.append(self._validate_syntax(test_file))
        self.results.append(self._validate_syntax(conftest_file))
        
        # Structure check
        sres = ValidationResult(f"Structure: {test_file.name}")
        if test_file.exists():
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())
                tcount = sum(1 for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name.startswith('test_'))
                if tcount == 0: sres.add_error("No test_ functions found")
                else: sres.add_warning(f"Found {tcount} tests")
            except Exception as e:
                sres.add_error(f"Structural error: {str(e)}")
        self.results.append(sres)
        
        return self.get_report()
    
    def get_report(self) -> Dict[str, Any]:
        total_passed = sum(1 for r in self.results if r.passed)
        total_errors = sum(len(r.errors) for r in self.results)
        
        return {
            'total_checks': len(self.results),
            'passed': total_passed,
            'failed': len(self.results) - total_passed,
            'total_errors': total_errors,
            'results': [r.to_dict() for r in self.results],
            'summary': 'PASSED' if total_errors == 0 else f'FAILED: {total_errors} errors'
        }
