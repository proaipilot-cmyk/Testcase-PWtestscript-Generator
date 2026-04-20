
"""
Parser Module - Converts test cases into structured format
Handles CSV parsing, normalization, and validation of test case data.
"""

import csv
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import re


class TestCaseParser:
    """
    Parses test cases from CSV/JSON format and structures them for downstream processing.
    
    Supports flexible header naming with automatic normalization to standard format:
    - id, title, precondition, steps, test_data, expected_result
    """
    
    # Header synonym mapping for flexible input
    HEADER_SYNONYMS = {
        "id": ["test case id", "test_case_id", "testcase id", "testcaseid", "tc_id", "id"],
        "title": ["test scenario description", "test_scenario_description", "title", "description", "test scenario"],
        "precondition": ["pre-condition", "precondition", "pre condition", "pre-conditions"],
        "steps": ["test steps", "test_steps", "steps", "actions"],
        "test_data": ["test data", "test_data", "testdata", "data"],
        "expected_result": ["expected result (er)", "expected result", "expected_result", "er", "expected results"]
    }
    
    def __init__(self, file_path: str):
        """
        Initialize parser with file path.
        
        Args:
            file_path: Path to test case file (CSV or JSON)
        """
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"Test case file not found: {file_path}")
        
        self.test_cases = []
        self.errors = []
        self.header_mapping = {}  # Maps logical names to actual CSV headers
    
    def parse(self) -> List[Dict[str, Any]]:
        """
        Parse test cases based on file extension.
        
        Returns:
            List of parsed test case dictionaries
        """
        if self.file_path.suffix.lower() == '.csv':
            return self._parse_csv()
        elif self.file_path.suffix.lower() == '.json':
            return self._parse_json()
        else:
            raise ValueError(f"Unsupported file format: {self.file_path.suffix}")
    
    def _normalize_headers(self, fieldnames: List[str]) -> Dict[str, str]:
        """
        Normalize CSV headers to standard format using synonym mapping.
        
        Args:
            fieldnames: List of CSV column headers
        
        Returns:
            Dictionary mapping standard names to actual CSV headers
            Example: {'id': 'Test Case ID', 'title': 'Test Scenario Description', ...}
        """
        # Create lowercase mapping for case-insensitive matching
        headers_lower = {h.strip().lower(): h.strip() for h in fieldnames}
        
        header_map = {}
        for standard_name, synonyms in self.HEADER_SYNONYMS.items():
            for synonym in synonyms:
                if synonym.lower() in headers_lower:
                    header_map[standard_name] = headers_lower[synonym.lower()]
                    break
        
        return header_map
    
    # ...existing code...
    def _normalize_headers(self, fieldnames: List[str]) -> Dict[str, str]:
        """
        Normalize CSV headers to standard format using synonym mapping.
        Cleans BOM, strips whitespace and ignores empty headers.
        """
        headers_lower = {}
        for h in fieldnames:
            if h is None:
                continue
            clean = h.strip().lstrip('\ufeff')
            if not clean:
                continue
            headers_lower[clean.lower()] = clean

        header_map = {}
        for standard_name, synonyms in self.HEADER_SYNONYMS.items():
            for synonym in synonyms:
                if synonym.lower() in headers_lower:
                    header_map[standard_name] = headers_lower[synonym.lower()]
                    break

        return header_map

    def _parse_csv(self) -> List[Dict[str, Any]]:
        """
        Parse CSV file containing test cases with flexible header normalization.
        Tries multiple encodings (utf-8-sig, utf-8, cp1252, latin-1) to avoid
        UnicodeDecodeError on files with BOM or non-utf8 bytes.
        """
        self.test_cases = []
        self.errors = []

        import csv
        from typing import Optional

        encodings_to_try = ["utf-8-sig", "utf-8", "cp1252", "latin-1"]
        last_exc: Optional[Exception] = None

        for enc in encodings_to_try:
            self.test_cases = []
            self.errors = []
            try:
                with open(self.file_path, 'r', encoding=enc, newline='') as file:
                    reader = csv.DictReader(file)
                    if reader.fieldnames is None:
                        raise ValueError("CSV file is empty or invalid")

                    # Normalize headers
                    self.header_mapping = self._normalize_headers(reader.fieldnames)

                    # Validate required columns
                    required_fields = {'id', 'title', 'steps'}
                    missing_fields = required_fields - set(self.header_mapping.keys())

                    if missing_fields:
                        available = list(reader.fieldnames)
                        raise ValueError(
                            f"Missing required columns: {missing_fields}\n"
                            f"Available headers: {available}\n"
                            f"Supported synonyms: {self.HEADER_SYNONYMS}"
                        )

                    for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is 1)
                        try:
                            normalized_row = self._normalize_row(row)
                            parsed_case = self._normalize_test_case(normalized_row, row_num)
                            self.test_cases.append(parsed_case)
                        except ValueError as e:
                            self.errors.append(f"Row {row_num}: {str(e)}")
                # success with this encoding
                last_exc = None
                break
            except UnicodeDecodeError as e:
                last_exc = e
                continue

        if last_exc:
            # none of the encodings worked
            raise last_exc

        return self.test_cases

    
    # def _parse_csv(self) -> List[Dict[str, Any]]:
    #     """
    #     Parse CSV file containing test cases with flexible header normalization.
        
    #     Returns:
    #         List of parsed test case dictionaries
    #     """
    #     self.test_cases = []
    #     self.errors = []
        
    #     try:
    #         with open(self.file_path, 'r', encoding='utf-8') as file:
    #             reader = csv.DictReader(file)
                
    #             if reader.fieldnames is None:
    #                 raise ValueError("CSV file is empty or invalid")
                
    #             # Normalize headers
    #             self.header_mapping = self._normalize_headers(reader.fieldnames)
                
    #             # Validate required columns
    #             required_fields = {'id', 'title', 'steps'}
    #             missing_fields = required_fields - set(self.header_mapping.keys())
                
    #             if missing_fields:
    #                 available = list(reader.fieldnames)
    #                 raise ValueError(
    #                     f"Missing required columns: {missing_fields}\n"
    #                     f"Available headers: {available}\n"
    #                     f"Supported synonyms: {self.HEADER_SYNONYMS}"
    #                 )
                
    #             for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is 1)
    #                 try:
    #                     # Normalize row using header mapping
    #                     normalized_row = self._normalize_row(row)
    #                     parsed_case = self._normalize_test_case(normalized_row, row_num)
    #                     self.test_cases.append(parsed_case)
    #                 except ValueError as e:
    #                     self.errors.append(f"Row {row_num}: {str(e)}")
        
    #     except IOError as e:
    #         raise IOError(f"Failed to read CSV file: {str(e)}")
        
    #     return self.test_cases
    
    def _normalize_row(self, raw_row: Dict[str, str]) -> Dict[str, str]:
        """
        Normalize a CSV row by mapping actual headers to standard names.
        
        Args:
            raw_row: Row dictionary with actual CSV headers as keys
        
        Returns:
            Row dictionary with standardized headers as keys
        """
        normalized = {}
        for standard_name, actual_header in self.header_mapping.items():
            normalized[standard_name] = raw_row.get(actual_header, "")
        
        # Preserve any additional columns not in mapping
        mapped_headers = set(self.header_mapping.values())
        for actual_header, value in raw_row.items():
            if actual_header not in mapped_headers and value and value.strip():
                # Store extra columns with lowercase key
                normalized[actual_header.lower()] = value
        
        return normalized
    
    def _parse_json(self) -> List[Dict[str, Any]]:
        """
        Parse JSON file containing test cases.
        
        Returns:
            List of parsed test case dictionaries
        """
        self.test_cases = []
        self.errors = []
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
                if not isinstance(data, list):
                    raise ValueError("JSON should contain a list of test cases")
                
                for idx, case in enumerate(data, start=1):
                    try:
                        if not isinstance(case, dict):
                            raise ValueError(f"Test case {idx} is not a dictionary")
                        
                        parsed_case = self._normalize_test_case(case, idx)
                        self.test_cases.append(parsed_case)
                    except ValueError as e:
                        self.errors.append(f"Case {idx}: {str(e)}")
        
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON format: {str(e)}", "", 0)
        except IOError as e:
            raise IOError(f"Failed to read JSON file: {str(e)}")
        
        return self.test_cases
    
    def _normalize_test_case(self, raw_case: Dict[str, str], row_num: int) -> Dict[str, Any]:
        """
        Normalize a single test case to standardized format.
        
        Args:
            raw_case: Raw test case dictionary with standardized headers
            row_num: Row/case number for error reporting
        
        Returns:
            Normalized test case dictionary
        """
        # Extract and validate required fields
        case_id = (raw_case.get('id') or '').strip()
        if not case_id:
            raise ValueError("Test case ID cannot be empty")
        
        title = (raw_case.get('title') or '').strip()
        if not title:
            raise ValueError(f"Test case '{case_id}' title cannot be empty")
        
        steps_raw = (raw_case.get('steps') or '').strip()
        if not steps_raw:
            raise ValueError(f"Test case '{case_id}' steps cannot be empty")
        
        # Parse steps (can be newline or semicolon separated)
        steps = self._parse_steps(steps_raw)
        if not steps:
            raise ValueError(f"Test case '{case_id}' has no valid steps after parsing")
        
        # Optional fields with defaults
        precondition = (raw_case.get('precondition') or '').strip()
        expected_result = (raw_case.get('expected_result') or '').strip()
        
        # Parse test data
        test_data = self._parse_test_data(raw_case.get('test_data', ''))
        
        return {
            'id': case_id,
            'title': title,
            'precondition': precondition,
            'steps': steps,
            'test_data': test_data,
            'expected_result': expected_result,
            'row_number': row_num,
            'human_approval': 'pending'
        }
    
    def _parse_steps(self, steps_raw: str) -> List[str]:
        """
        Parse steps from various formats (newline-separated, number-prefixed, etc).
        
        Args:
            steps_raw: Raw steps string
        
        Returns:
            List of individual steps with numbering removed
        """
        if not steps_raw:
            return []
        
        # Split by newlines first
        lines = steps_raw.split('\n')
        
        steps = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Remove numbering like "1.", "2.", etc. and leading/trailing whitespace
            cleaned = re.sub(r'^\d+\.\s*', '', line).strip()
            if cleaned:
                steps.append(cleaned)
        
        return steps
    
    def _parse_test_data(self, test_data_raw: str) -> Dict[str, str]:
        """
        Parse test data from various formats (comma or newline separated key:value pairs).
        
        Args:
            test_data_raw: Raw test data string
        
        Returns:
            Dictionary of test data key-value pairs
        """
        test_data = {}
        
        if not test_data_raw:
            return test_data
        
        # Split by commas, newlines, or both - handles: "key: value, key: value" and "key: value\nkey: value"
        entries = re.split(r'[,\n]+', test_data_raw)
        
        for entry in entries:
            entry = entry.strip()
            if not entry or entry == "N/A":
                continue
            
            # Parse key:value format
            if ':' in entry:
                key, value = entry.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Handle empty values marked as (empty)
                if value.lower() == "(empty)":
                    value = ""
                
                if key:
                    test_data[key] = value
        
        return test_data
    
    def get_test_cases(self) -> List[Dict[str, Any]]:
        """Get parsed test cases."""
        return self.test_cases
    
    def get_errors(self) -> List[str]:
        """Get parsing errors encountered."""
        return self.errors
    
    def has_errors(self) -> bool:
        """Check if any errors occurred during parsing."""
        return len(self.errors) > 0
    
    def get_header_mapping(self) -> Dict[str, str]:
        """Get the mapping of standard names to actual CSV headers used."""
        return self.header_mapping
    
    def to_json(self, output_path: Optional[str] = None) -> str:
        """
        Convert parsed test cases to JSON format.
        
        Args:
            output_path: Optional path to save JSON output
        
        Returns:
            JSON string representation
        """
        json_str = json.dumps(self.test_cases, indent=2, ensure_ascii=False)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(json_str)
        
        return json_str


def parse_test_cases(file_path: str) -> tuple[List[Dict[str, Any]], List[str]]:
    """
    Convenience function to parse test cases from a file.
    
    Args:
        file_path: Path to test case file
    
    Returns:
        Tuple of (parsed_cases, errors)
    """
    parser = TestCaseParser(file_path)
    cases = parser.parse()
    errors = parser.get_errors()
    
    return cases, errors


# """
# Parser Module - Converts test cases into structured format
# Handles CSV parsing, normalization, and validation of test case data.
# """

# import csv
# import json
# from pathlib import Path
# from typing import List, Dict, Any, Optional
# import re


# class TestCaseParser:
#     """
#     Parses test cases from CSV/JSON format and structures them for downstream processing.
    
#     Expected CSV columns: id, title, precondition, steps, test_data, expected_result
#     """
    
#     def __init__(self, file_path: str):
#         """
#         Initialize parser with file path.
        
#         Args:
#             file_path: Path to test case file (CSV or JSON)
#         """
#         self.file_path = Path(file_path)
#         if not self.file_path.exists():
#             raise FileNotFoundError(f"Test case file not found: {file_path}")
        
#         self.test_cases = []
#         self.errors = []
    
#     def parse(self) -> List[Dict[str, Any]]:
#         """
#         Parse test cases based on file extension.
        
#         Returns:
#             List of parsed test case dictionaries
#         """
#         if self.file_path.suffix.lower() == '.csv':
#             return self._parse_csv()
#         elif self.file_path.suffix.lower() == '.json':
#             return self._parse_json()
#         else:
#             raise ValueError(f"Unsupported file format: {self.file_path.suffix}")
    
#     def _parse_csv(self) -> List[Dict[str, Any]]:
#         """
#         Parse CSV file containing test cases.
        
#         Returns:
#             List of parsed test case dictionaries
#         """
#         self.test_cases = []
#         self.errors = []
        
#         try:
#             with open(self.file_path, 'r', encoding='utf-8') as file:
#                 reader = csv.DictReader(file)
                
#                 if reader.fieldnames is None:
#                     raise ValueError("CSV file is empty or invalid")
                
#                 # Validate required columns
#                 required_columns = {'id', 'title', 'steps'}
#                 missing_columns = required_columns - set(reader.fieldnames)
#                 if missing_columns:
#                     raise ValueError(f"Missing required columns: {missing_columns}")
                
#                 for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is 1)
#                     try:
#                         parsed_case = self._normalize_test_case(row, row_num)
#                         self.test_cases.append(parsed_case)
#                     except ValueError as e:
#                         self.errors.append(f"Row {row_num}: {str(e)}")
        
#         except IOError as e:
#             raise IOError(f"Failed to read CSV file: {str(e)}")
        
#         return self.test_cases
    
#     def _parse_json(self) -> List[Dict[str, Any]]:
#         """
#         Parse JSON file containing test cases.
        
#         Returns:
#             List of parsed test case dictionaries
#         """
#         self.test_cases = []
#         self.errors = []
        
#         try:
#             with open(self.file_path, 'r', encoding='utf-8') as file:
#                 data = json.load(file)
                
#                 if not isinstance(data, list):
#                     raise ValueError("JSON should contain a list of test cases")
                
#                 for idx, case in enumerate(data, start=1):
#                     try:
#                         if not isinstance(case, dict):
#                             raise ValueError(f"Test case {idx} is not a dictionary")
                        
#                         parsed_case = self._normalize_test_case(case, idx)
#                         self.test_cases.append(parsed_case)
#                     except ValueError as e:
#                         self.errors.append(f"Case {idx}: {str(e)}")
        
#         except json.JSONDecodeError as e:
#             raise json.JSONDecodeError(f"Invalid JSON format: {str(e)}", "", 0)
#         except IOError as e:
#             raise IOError(f"Failed to read JSON file: {str(e)}")
        
#         return self.test_cases
    
#     def _normalize_test_case(self, raw_case: Dict[str, str], row_num: int) -> Dict[str, Any]:
#         """
#         Normalize a single test case to standardized format.
        
#         Args:
#             raw_case: Raw test case dictionary from CSV/JSON
#             row_num: Row/case number for error reporting
        
#         Returns:
#             Normalized test case dictionary
#         """
#         # Extract and validate required fields
#         case_id = (raw_case.get('id') or '').strip()
#         if not case_id:
#             raise ValueError("Test case ID cannot be empty")
        
#         title = (raw_case.get('title') or '').strip()
#         if not title:
#             raise ValueError(f"Test case '{case_id}' title cannot be empty")
        
#         steps_raw = (raw_case.get('steps') or '').strip()
#         if not steps_raw:
#             raise ValueError(f"Test case '{case_id}' steps cannot be empty")
        
#         # Parse steps (can be newline or semicolon separated)
#         steps = self._parse_steps(steps_raw)
#         if not steps:
#             raise ValueError(f"Test case '{case_id}' has no valid steps after parsing")
        
#         # Optional fields with defaults
#         precondition = (raw_case.get('precondition') or '').strip()
#         expected_result = (raw_case.get('expected_result') or '').strip()
        
#         # Parse test data
#         test_data = self._parse_test_data(raw_case.get('test_data', ''))
        
#         return {
#             'id': case_id,
#             'title': title,
#             'precondition': precondition,
#             'steps': steps,
#             'test_data': test_data,
#             'expected_result': expected_result,
#             'row_number': row_num
#         }
    
#     def _parse_steps(self, steps_raw: str) -> List[str]:
#         """
#         Parse steps from various formats (newline-separated, number-prefixed, etc).
        
#         Args:
#             steps_raw: Raw steps string
        
#         Returns:
#             List of individual steps
#         """
#         if not steps_raw:
#             return []
        
#         # Split by newlines first
#         lines = steps_raw.split('\n')
        
#         steps = []
#         for line in lines:
#             line = line.strip()
#             if not line:
#                 continue
            
#             # Remove numbering like "1.", "2.", etc.
#             cleaned = re.sub(r'^\d+\.\s*', '', line)
#             if cleaned:
#                 steps.append(cleaned)
        
#         return steps
    
#     def _parse_test_data(self, test_data_raw: str) -> Dict[str, str]:
#         """
#         Parse test data from comma-separated key:value pairs.
        
#         Args:
#             test_data_raw: Raw test data string
        
#         Returns:
#             Dictionary of test data key-value pairs
#         """
#         test_data = {}
        
#         if not test_data_raw:
#             return test_data
        
#         # Handle both comma and newline separated formats
#         entries = re.split(r'[,\n]', test_data_raw)
        
#         for entry in entries:
#             entry = entry.strip()
#             if not entry:
#                 continue
            
#             # Parse key:value format
#             if ':' in entry:
#                 key, value = entry.split(':', 1)
#                 test_data[key.strip()] = value.strip()
        
#         return test_data
    
#     def get_test_cases(self) -> List[Dict[str, Any]]:
#         """Get parsed test cases."""
#         return self.test_cases
    
#     def get_errors(self) -> List[str]:
#         """Get parsing errors encountered."""
#         return self.errors
    
#     def has_errors(self) -> bool:
#         """Check if any errors occurred during parsing."""
#         return len(self.errors) > 0
    
#     def to_json(self, output_path: Optional[str] = None) -> str:
#         """
#         Convert parsed test cases to JSON format.
        
#         Args:
#             output_path: Optional path to save JSON output
        
#         Returns:
#             JSON string representation
#         """
#         json_str = json.dumps(self.test_cases, indent=2)
        
#         if output_path:
#             with open(output_path, 'w', encoding='utf-8') as f:
#                 f.write(json_str)
        
#         return json_str


# def parse_test_cases(file_path: str) -> tuple[List[Dict[str, Any]], List[str]]:
#     """
#     Convenience function to parse test cases from a file.
    
#     Args:
#         file_path: Path to test case file
    
#     Returns:
#         Tuple of (parsed_cases, errors)
#     """
#     parser = TestCaseParser(file_path)
#     cases = parser.parse()
#     errors = parser.get_errors()
    
#     return cases, errors
