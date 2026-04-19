"""
Validator Module - Comprehensive syntax, structure, and quality validation
of generated POM framework code.
"""

import ast
import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional


class ValidationResult:
    """Container for validation results."""
    
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


class SyntaxValidator:
    """Validate Python syntax using AST parsing."""
    
    @staticmethod
    def validate_file(file_path: Path) -> ValidationResult:
        """Validate Python file syntax."""
        result = ValidationResult(f"Syntax: {file_path.name}")
        
        if not file_path.exists():
            result.add_error(f"File not found: {file_path}")
            return result
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            # Try to parse with AST
            ast.parse(source)
            result.add_warning(f"✓ Valid Python syntax")
        
        except SyntaxError as e:
            result.add_error(f"Syntax error at line {e.lineno}: {e.msg}")
        except Exception as e:
            result.add_error(f"Parse error: {str(e)}")
        
        return result


class ImportValidator:
    """Validate that all imports can be resolved."""
    
    @staticmethod
    def validate_file(file_path: Path, base_dir: Path) -> ValidationResult:
        """Validate imports in a Python file."""
        result = ValidationResult(f"Imports: {file_path.name}")
        
        if not file_path.exists():
            result.add_error(f"File not found: {file_path}")
            return result
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source)
            imports = []
            
            # Extract all imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
            
            # Check standard library imports
            stdlib = {
                'pytest', 'asyncio', 'json', 'pathlib', 'typing', 'datetime',
                'logging', 'sys', 'os', 're', 'csv', 'abc', 'dataclasses'
            }
            
            for imp in imports:
                root_module = imp.split('.')[0]
                
                # Check if custom module exists
                if root_module not in stdlib:
                    custom_path = base_dir / f"{root_module}.py"
                    pkg_path = base_dir / root_module / "__init__.py"
                    
                    if not custom_path.exists() and not pkg_path.exists():
                        result.add_warning(f"Custom module '{root_module}' not found (may be external)")
                    else:
                        result.add_warning(f"✓ Import '{imp}' found")
        
        except Exception as e:
            result.add_error(f"Import validation error: {str(e)}")
        
        return result


class FixtureValidator:
    """Validate pytest fixtures."""
    
    @staticmethod
    def validate_conftest(conftest_path: Path) -> ValidationResult:
        """Validate conftest.py fixtures."""
        result = ValidationResult("Fixtures: conftest.py")
        
        if not conftest_path.exists():
            result.add_error(f"conftest.py not found at {conftest_path}")
            return result
        
        try:
            with open(conftest_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source)
            fixtures = []
            
            # Extract fixture definitions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check for @pytest.fixture decorator
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Attribute):
                            if decorator.attr == 'fixture':
                                fixtures.append(node.name)
                        elif isinstance(decorator, ast.Name):
                            if decorator.id == 'fixture':
                                fixtures.append(node.name)
            
            if not fixtures:
                result.add_warning("No fixtures found (may be in conftest)")
            else:
                for fixture in fixtures:
                    result.add_warning(f"✓ Fixture '{fixture}' defined")
        
        except Exception as e:
            result.add_error(f"Fixture validation error: {str(e)}")
        
        return result
    
    @staticmethod
    def validate_test_file(test_file: Path, conftest_path: Path) -> ValidationResult:
        """Validate test file uses fixtures correctly."""
        result = ValidationResult(f"Test Fixtures: {test_file.name}")
        
        if not test_file.exists():
            result.add_error(f"Test file not found: {test_file}")
            return result
        
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source)
            test_functions = []
            
            # Extract test functions
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith('test_'):
                    # Check parameters (should include browser_context)
                    params = [arg.arg for arg in node.args.args]
                    if 'browser_context' not in params:
                        result.add_warning(f"Test '{node.name}' missing 'browser_context' fixture")
                    else:
                        result.add_warning(f"✓ Test '{node.name}' uses browser_context fixture")
        
        except Exception as e:
            result.add_error(f"Test fixture validation error: {str(e)}")
        
        return result


class JSONValidator:
    """Validate JSON structure files."""
    
    @staticmethod
    def validate_file(json_path: Path) -> ValidationResult:
        """Validate JSON file structure."""
        result = ValidationResult(f"JSON: {json_path.name}")
        
        if not json_path.exists():
            result.add_error(f"File not found: {json_path}")
            return result
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate structure
            if 'page_name' not in data:
                result.add_warning("Missing 'page_name' field")
            
            if 'elements' not in data:
                result.add_error("Missing required 'elements' field")
            else:
                elements = data['elements']
                for elem_name, elem_def in elements.items():
                    if 'selector' not in elem_def:
                        result.add_error(f"Element '{elem_name}' missing 'selector'")
                    if 'type' not in elem_def:
                        result.add_warning(f"Element '{elem_name}' missing 'type'")
            
            result.add_warning(f"✓ Valid JSON structure ({len(data.get('elements', {}))} elements)")
        
        except json.JSONDecodeError as e:
            result.add_error(f"JSON decode error: {e}")
        except Exception as e:
            result.add_error(f"JSON validation error: {str(e)}")
        
        return result


class StructureValidator:
    """Validate test structure and best practices."""
    
    @staticmethod
    def validate_test_file(test_file: Path) -> ValidationResult:
        """Validate test structure."""
        result = ValidationResult(f"Structure: {test_file.name}")
        
        if not test_file.exists():
            result.add_error(f"File not found: {test_file}")
            return result
        
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source)
            test_count = 0
            imports_present = False
            
            # Check imports
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    imports_present = True
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith('test_'):
                    test_count += 1
                    
                    # Check test has docstring
                    docstring = ast.get_docstring(node)
                    if not docstring:
                        result.add_warning(f"Test '{node.name}' missing docstring")
                    
                    # Check test has try/finally for cleanup
                    has_finally = any(
                        isinstance(child, ast.Try) and child.finalbody
                        for child in ast.walk(node)
                    )
                    if not has_finally:
                        result.add_warning(f"Test '{node.name}' missing finally block (no cleanup)")
            
            if not imports_present:
                result.add_error("No imports found in test file")
            
            if test_count == 0:
                result.add_error("No test functions found (must start with 'test_')")
            else:
                result.add_warning(f"✓ Found {test_count} test functions")
        
        except Exception as e:
            result.add_error(f"Structure validation error: {str(e)}")
        
        return result


class Validator:
    """Main validator orchestrator."""
    
    def __init__(self, base_dir: Path = None):
        """Initialize validator."""
        self.base_dir = base_dir or Path('.')
        self.results: List[ValidationResult] = []
    
    def validate_generated_framework(self) -> Dict[str, Any]:
        """Validate entire generated framework."""
        
        # Syntax validation
        self.results.append(SyntaxValidator.validate_file(self.base_dir / 'tests' / 'test_automation.py'))
        self.results.append(SyntaxValidator.validate_file(self.base_dir / 'tests' / 'conftest.py'))
        self.results.append(SyntaxValidator.validate_file(self.base_dir / 'steps' / 'steps.py'))
        self.results.append(SyntaxValidator.validate_file(self.base_dir / 'pages' / 'base_page.py'))
        self.results.append(SyntaxValidator.validate_file(self.base_dir / 'pages' / 'login_page.py'))
        
        # Import validation
        self.results.append(ImportValidator.validate_file(
            self.base_dir / 'tests' / 'test_automation.py',
            self.base_dir
        ))
        self.results.append(ImportValidator.validate_file(
            self.base_dir / 'steps' / 'steps.py',
            self.base_dir
        ))
        
        # Fixture validation
        self.results.append(FixtureValidator.validate_conftest(self.base_dir / 'tests' / 'conftest.py'))
        self.results.append(FixtureValidator.validate_test_file(
            self.base_dir / 'tests' / 'test_automation.py',
            self.base_dir / 'tests' / 'conftest.py'
        ))
        
        # JSON validation
        for json_file in (self.base_dir / 'object_repo').glob('*.json'):
            self.results.append(JSONValidator.validate_file(json_file))
        
        # Structure validation
        self.results.append(StructureValidator.validate_test_file(self.base_dir / 'tests' / 'test_automation.py'))
        
        return self.get_report()
    
    
    def get_report(self) -> Dict[str, Any]:
        """Generate validation report."""
        total_passed = sum(1 for r in self.results if r.passed)
        # Some ValidationResult instances may not expose numeric counts
        # (older versions or different implementations). Compute counts
        # robustly by preferring explicit attributes then falling back
        # to the lengths of `errors`/`warnings` lists.
        def _count_errors(rr: ValidationResult) -> int:
            if hasattr(rr, 'error_count'):
                try:
                    return int(getattr(rr, 'error_count'))
                except Exception:
                    pass
            return len(getattr(rr, 'errors', []) or [])

        def _count_warnings(rr: ValidationResult) -> int:
            if hasattr(rr, 'warning_count'):
                try:
                    return int(getattr(rr, 'warning_count'))
                except Exception:
                    pass
            return len(getattr(rr, 'warnings', []) or [])

        total_errors = sum(_count_errors(r) for r in self.results)
        total_warnings = sum(_count_warnings(r) for r in self.results)
        
        return {
            'timestamp': str(Path.cwd()),
            'total_checks': len(self.results),
            'passed': total_passed,
            'failed': len(self.results) - total_passed,
            'total_errors': total_errors,
            'total_warnings': total_warnings,
            'results': [r.to_dict() for r in self.results],
            'summary': 'ALL CHECKS PASSED ✅' if total_errors == 0 else f'VALIDATION FAILED: {total_errors} errors'
        }
