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
    """

    # Generic patterns for common web actions
    PATTERNS = [
        (re.compile(r'\b(launch|open|navigate to|goto|visit)\b.*(http[s]?://\S+)', re.I), 'goto'),
        (re.compile(r'\b(launch|open|navigate to|goto|visit|at)\b.*(homepage|index|login)', re.I), 'goto_base'),
        (re.compile(r'\b(enter|type|input|fill)\b.*(username|user\s*id|email|login)', re.I), 'fill_username'),
        (re.compile(r'\b(enter|type|input|fill)\b.*password', re.I), 'fill_password'),
        (re.compile(r'\b(click|press|tap)\b.*(login|sign\s*in|submit|connect)', re.I), 'click_login'),
        (re.compile(r'\b(click|press|tap)\b.*(button|link|icon|menu)\b', re.I), 'click_generic'),
        (re.compile(r'\b(add\s*to\s*cart|buy|purchase|remove|delete)\b', re.I), 'click_action'),
        (re.compile(r'\b(verify|check|observe|ensure|assert|confirm|should\s*be|appears|shown|displayed)\b', re.I), 'assert'),
        (re.compile(r'\b(error|invalid|failed|denied|sorry|wrong|incorrect|mismatch)\b', re.I), 'assert_error'),
        (re.compile(r'\bscroll\b', re.I), 'scroll'),
    ]

    def __init__(self):
        self.default_url = "https://www.saucedemo.com" # Fallback for demo, but can be overridden

    def plan_case(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a single normalized test case into the canonical action schema."""
        actions: List[Dict[str, Any]] = []
        td = self._normalize_test_data(test_case.get("test_data", {}))
        
        # Try to find a URL in the precondition
        precondition = test_case.get("precondition", "")
        url_match = re.search(r'(https?://\S+)', precondition)
        if url_match:
            self.default_url = url_match.group(1)

        # Process each step
        for step_idx, step in enumerate(test_case.get("steps", []), start=1):
            step = step.strip()
            if not step:
                continue

            # Check for inline data
            self._inject_inline_testdata(step, td)

            # Pattern matching
            matched = False
            for pattern, action_type in self.PATTERNS:
                m = pattern.search(step)
                if m:
                    action = self._make_action(action_type, step, td, m)
                    actions.append(action)
                    matched = True
                    break
            
            if not matched:
                # Fallback heuristics
                if re.search(r'http[s]?://', step, re.I):
                    m = re.search(r'(http[s]?://\S+)', step, re.I)
                    actions.append({'type': 'goto', 'url': m.group(1) if m else self.default_url, 'raw': step})
                elif re.search(r'(enter|type|fill)\s+', step, re.I):
                    field = self._infer_field(step)
                    value = td.get(field, "")
                    actions.append({'type': 'fill', 'field': field, 'value': value, 'raw': step})
                elif re.search(r'(click|press|tap)\s+', step, re.I):
                    target = self._infer_target(step)
                    actions.append({'type': 'click', 'target': target, 'raw': step})
                else:
                    actions.append({'type': 'note', 'raw': step})

        # Add expected_result as final assertion
        er = (test_case.get("expected_result") or "").strip()
        if er:
            actions.append({'type': 'assert_text', 'text': er})

        return {
            'id': test_case.get('id'),
            'title': test_case.get('title'),
            'precondition': precondition,
            'actions': actions,
            'expected_result': er
        }

    def plan_cases(self, cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [self.plan_case(c) for c in cases]

    def _normalize_test_data(self, td: Any) -> Dict[str, str]:
        if isinstance(td, dict):
            src = td
        elif isinstance(td, str):
            src = {}
            for line in td.splitlines():
                if ':' in line:
                    k, v = line.split(':', 1)
                    src[k.strip().lower()] = v.strip()
        else:
            src = {}
        return {k.replace(' ', '_').lower(): str(v).strip() for k, v in src.items()}

    def _inject_inline_testdata(self, step: str, td: Dict[str, str]) -> None:
        patterns = {
            'username': [r'username\s*[:\-]\s*(\S+)', r'email\s*[:\-]\s*(\S+@\S+)'],
            'password': [r'password\s*[:\-]\s*(\S+)']
        }
        for key, p_list in patterns.items():
            for p in p_list:
                m = re.search(p, step, re.I)
                if m:
                    td[key] = m.group(1).strip().strip('"\'')

    def _infer_field(self, step: str) -> str:
        for f in ['username', 'password', 'email', 'phone', 'address', 'city']:
            if f in step.lower(): return f
        return 'value'

    def _infer_target(self, step: str) -> str:
        m = re.search(r'(click|press|tap)\s+(?:on\s+)?(?:the\s+)?(.+?)(?:\s+(button|link|icon))?$', step, re.I)
        return m.group(2).strip().replace(' ', '-').lower() if m else 'button'

    def _make_action(self, atype: str, step: str, td: Dict[str, str], match: re.Match) -> Dict[str, Any]:
        if atype == 'goto':
            return {'type': 'goto', 'url': match.group(2), 'raw': step}
        if atype == 'goto_base':
            return {'type': 'goto', 'url': self.default_url, 'raw': step}
        if atype == 'fill_username':
            return {'type': 'fill', 'field': 'username', 'value': td.get('username', td.get('email', '')), 'raw': step}
        if atype == 'fill_password':
            return {'type': 'fill', 'field': 'password', 'value': td.get('password', ''), 'raw': step}
        if atype == 'click_login':
            return {'type': 'click', 'target': 'login-button', 'raw': step}
        if atype == 'click_generic' or atype == 'click_action':
            target = self._infer_target(step)
            return {'type': 'click', 'target': target, 'raw': step}
        if atype == 'assert' or atype == 'assert_error':
            return {'type': 'assert_text', 'text': step, 'raw': step}
        if atype == 'scroll':
            return {'type': 'scroll', 'direction': 'down' if 'down' in step.lower() else 'up', 'raw': step}
        return {'type': 'note', 'raw': step}


def plan_test_cases(cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return Planner().plan_cases(cases)
