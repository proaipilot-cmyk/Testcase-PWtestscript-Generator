"""
Rule-based Planner Module - Converts test cases into canonical action schema
Emits framework-agnostic actions that generator adapters can consume.
"""

import re
from typing import List, Dict, Any, Optional


class Planner:
    """
    Rule-based planner that converts normalized test-case dicts (from parser)
    into a canonical action schema suitable for generator adapters.

    Canonical action format examples:
      {'type': 'goto', 'url': 'https://www.saucedemo.com'}
      {'type': 'fill', 'field': 'username', 'value': 'standard_user'}
      {'type': 'click', 'target': 'login_button'}
      {'type': 'assert_text', 'text': 'Products'}
      {'type': 'note', 'raw': 'unrecognized step'}
    """

    # Simple regex -> action_type mapping (order matters - first match wins)
    PATTERNS = [
        (re.compile(r'\b(launch|open|navigate to).*(http[s]?://\S+|saucedemo)', re.I), 'goto'),
        (re.compile(r'\benter\b.*username', re.I), 'fill_username'),
        (re.compile(r'\benter\b.*password', re.I), 'fill_password'),
        (re.compile(r'\bclick\b.*login', re.I), 'click_login'),
        (re.compile(r'\bclick\b.*(button|link)\b', re.I), 'click_generic'),
        (re.compile(r'\b(add to cart|remove)\b', re.I), 'click_generic'),
        (re.compile(r'\b(verify|check|observe|ensure|assert|confirm)\b', re.I), 'assert'),
        (re.compile(r'\b(error message|sorry|epic sadface)\b', re.I), 'assert_error'),
        (re.compile(r'\b(redirected|displayed|shown|appears)\b', re.I), 'assert_text'),
        (re.compile(r'\bscroll\b', re.I), 'scroll'),
    ]

    DEFAULT_SITE = "https://www.saucedemo.com"

    def __init__(self):
        """Initialize planner."""
        self.actions_log = []

    def plan_case(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert a single normalized test case into the canonical action schema.
        
        Expects test_case keys at least: 'id', 'title', 'steps', 'test_data', 'expected_result'
        
        Returns:
            Dict with keys: id, title, actions (List[Dict]), precondition
        """
        actions: List[Dict[str, Any]] = []
        td = self._normalize_test_data(test_case.get("test_data", {}))

        # Process each step
        for step_idx, step in enumerate(test_case.get("steps", []), start=1):
            step = step.strip()
            if not step:
                continue

            # Extract inline key:value pairs (e.g., "Enter Username: locked_out_user")
            self._inject_inline_testdata(step, td)

            # Try pattern matching first
            matched = False
            for pattern, action_type in self.PATTERNS:
                if pattern.search(step):
                    action = self._make_action(action_type, step, td)
                    actions.append(action)
                    matched = True
                    break
            
            # Fallback heuristics if no pattern matched
            if not matched:
                if re.search(r'http[s]?://', step, re.I):
                    m = re.search(r'(http[s]?://\S+)', step, re.I)
                    if m:
                        actions.append({'type': 'goto', 'url': m.group(1), 'raw': step})
                    else:
                        actions.append({'type': 'goto', 'url': self.DEFAULT_SITE, 'raw': step})
                elif re.search(r'enter\s+', step, re.I):
                    field = self._infer_field(step)
                    value = td.get(field, "")
                    actions.append({'type': 'fill', 'field': field, 'value': value, 'raw': step})
                else:
                    actions.append({'type': 'note', 'raw': step})

        # Add expected_result as final assertion if present
        er = (test_case.get("expected_result") or "").strip()
        if er:
            actions.append({'type': 'assert_text', 'text': er})

        return {
            'id': test_case.get('id'),
            'title': test_case.get('title'),
            'precondition': test_case.get('precondition', ''),
            'actions': actions,
            'expected_result': er
        }

    def plan_cases(self, cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Plan multiple test cases.
        
        Args:
            cases: List of test case dicts from parser
        
        Returns:
            List of planned test cases with canonical actions
        """
        return [self.plan_case(c) for c in cases]

    def _normalize_test_data(self, td: Any) -> Dict[str, str]:
        """
        Normalize test_data keys to lowercase simple keys.
        Examples:
          "Username" -> "username"
          "Password" -> "password"
        
        Accepts dict or string (attempts simple "k: v" line parsing).
        """
        if isinstance(td, dict):
            src = td
        elif isinstance(td, str):
            src = {}
            for line in td.splitlines():
                if ':' in line:
                    k, v = line.split(':', 1)
                    src[k.strip()] = v.strip()
        else:
            src = {}

        norm = {}
        for k, v in src.items():
            # Normalize key: lowercase, replace spaces/underscores with underscore
            key = re.sub(r'[\s\-]+', '_', k.strip().lower())
            # Handle (empty) placeholder
            val = str(v).strip()
            norm[key] = "" if val.lower() == "(empty)" else val
        return norm

    def _inject_inline_testdata(self, step: str, td: Dict[str, str]) -> None:
        """
        If step contains inline data like 'Enter Username: locked_out_user',
        extract and put it into td so subsequent fills use the inline value.
        """
        # Username pattern: "Enter Username: value"
        m = re.search(r'username\s*[:\-]\s*(\S+)', step, re.I)
        if m:
            td['username'] = m.group(1).strip().strip('"').strip("'")

        # Password pattern: "Enter Password: value"
        m2 = re.search(r'password\s*[:\-]\s*(\S+)', step, re.I)
        if m2:
            td['password'] = m2.group(1).strip().strip('"').strip("'")

        # Email pattern
        m3 = re.search(r'email\s*[:\-]\s*(\S+@\S+)', step, re.I)
        if m3:
            td['email'] = m3.group(1).strip()

    def _infer_field(self, step: str) -> str:
        """Infer field name from step text."""
        if re.search(r'username', step, re.I):
            return 'username'
        if re.search(r'password', step, re.I):
            return 'password'
        if re.search(r'email', step, re.I):
            return 'email'
        if re.search(r'url|link', step, re.I):
            return 'url'
        return 'value'

    def _make_action(self, action_type: str, step: str, td: Dict[str, str]) -> Dict[str, Any]:
        """
        Construct canonical action dicts by action_type.
        
        Args:
            action_type: Type of action to create
            step: Original step text for reference
            td: Test data dict
        
        Returns:
            Action dict with canonical schema
        """
        action_type = action_type.lower()

        if action_type == 'goto':
            # Extract URL or use default site
            m = re.search(r'(http[s]?://\S+|saucedemo)', step, re.I)
            url = self.DEFAULT_SITE
            if m:
                u = m.group(1)
                if 'saucedemo' in u and not u.startswith('http'):
                    url = self.DEFAULT_SITE
                else:
                    url = u
            return {'type': 'goto', 'url': url, 'raw': step}

        if action_type == 'fill_username':
            return {
                'type': 'fill',
                'field': 'username',
                'value': td.get('username', ''),
                'raw': step
            }

        if action_type == 'fill_password':
            return {
                'type': 'fill',
                'field': 'password',
                'value': td.get('password', ''),
                'raw': step
            }

        if action_type == 'click_login':
            return {
                'type': 'click',
                'target': 'login_button',
                'raw': step
            }

        if action_type == 'click_generic':
            # Extract target button/link name from step
            m = re.search(r'click\s+(?:on\s+)?(?:the\s+)?(.+?)(?:\s+button)?$', step, re.I)
            target = (m.group(1).strip() if m else 'button')
            return {
                'type': 'click',
                'target': target,
                'raw': step
            }

        if action_type == 'assert':
            return {
                'type': 'assert_text',
                'text': step,
                'raw': step
            }

        if action_type == 'assert_error':
            payload = {
                'type': 'assert_error',
                'text': step,
                'raw': step
            }
            # Try to extract quoted error message
            qm = re.search(r'["\']([^"\']+)["\']', step)
            if qm:
                payload['text'] = qm.group(1)
            return payload

        if action_type == 'assert_text':
            return {
                'type': 'assert_text',
                'text': step,
                'raw': step
            }

        if action_type == 'scroll':
            direction = 'down'
            if re.search(r'up', step, re.I):
                direction = 'up'
            return {
                'type': 'scroll',
                'direction': direction,
                'raw': step
            }

        return {'type': 'note', 'raw': step}


def plan_test_cases(cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convenience function to plan multiple test cases.
    
    Args:
        cases: List of parsed test case dicts from parser
    
    Returns:
        List of planned cases with canonical actions
    """
    planner = Planner()
    return planner.plan_cases(cases)
