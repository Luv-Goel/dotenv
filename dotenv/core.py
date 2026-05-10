"""Dotenv — .env file toolkit core."""

import os
import re
from typing import List, Dict, Optional, Tuple


def parse_env(content: str) -> List[Dict]:
    """Parse .env file content into structured entries."""
    entries = []
    for i, line in enumerate(content.split("\n"), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            entries.append({"line": i, "type": "comment" if stripped.startswith("#") else "blank",
                            "raw": line})
            continue

        # Check for export prefix
        has_export = stripped.startswith("export ")
        if has_export:
            stripped = stripped[7:].strip()

        # Split on first = 
        match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.*)', stripped)
        if match:
            key = match.group(1)
            value = match.group(2)
            quoted = False
            quote_char = None
            if (value.startswith('"') and value.endswith('"')) or \
               (value.startswith("'") and value.endswith("'")):
                quoted = True
                quote_char = value[0]
                value = value[1:-1]
            entries.append({
                "line": i, "type": "var", "key": key, "value": value,
                "raw": line, "export": has_export, "quoted": quoted,
                "quote_char": quote_char,
            })
        else:
            entries.append({"line": i, "type": "var", "key": stripped.split("=")[0] if "=" in stripped else stripped,
                            "raw": line, "parse_error": True})

    return entries


def load_env(path: str) -> List[Dict]:
    """Load and parse a .env file."""
    with open(path, "r", encoding="utf-8") as f:
        return parse_env(f.read())


def get_variables(entries: List[Dict]) -> Dict[str, str]:
    """Extract key-value pairs from parsed entries."""
    return {e["key"]: e.get("value", "") for e in entries if e["type"] == "var" and "parse_error" not in e}


def check_env(entries: List[Dict]) -> List[str]:
    """Check for common .env issues."""
    issues = []
    seen_keys = {}
    for e in entries:
        if e["type"] == "var":
            key = e["key"]
            # Duplicate check
            if key in seen_keys:
                issues.append(f"Line {e['line']}: Duplicate key '{key}' (was line {seen_keys[key]})")
            seen_keys[key] = seen_keys.get(key, e["line"])

            # Check for parse errors
            if e.get("parse_error"):
                issues.append(f"Line {e['line']}: Parse error — '{e['raw'].strip()}'")

            # Check for unquoted values with special chars
            val = e.get("value", "")
            if not e.get("quoted") and any(c in val for c in " #'\"") and val:
                issues.append(f"Line {e['line']}: Unquoted value with special chars — consider quoting")

            # Check for trailing whitespace in value
            raw = e["raw"]
            if "=" in raw:
                after_eq = raw.split("=", 1)[1]
                if after_eq != after_eq.rstrip():
                    issues.append(f"Line {e['line']}: Trailing whitespace in value")

            # Warn on empty values
            if not val.strip():
                issues.append(f"Line {e['line']}: Empty value for '{key}'")

    return issues


def generate_template(entries: List[Dict]) -> str:
    """Generate .env.example from parsed entries."""
    lines = []
    for e in entries:
        if e["type"] == "comment":
            lines.append(e["raw"])
        elif e["type"] == "blank":
            lines.append("")
        elif e["type"] == "var":
            key = e["key"]
            val = e.get("value", "")
            if val:
                lines.append(f"{key}=")
            else:
                lines.append(f"{key}=")
    return "\n".join(lines)


def merge_envs(primary: List[Dict], secondary: List[Dict]) -> List[Dict]:
    """Merge two .env files (primary takes precedence)."""
    primary_keys = {e["key"] for e in primary if e["type"] == "var"}
    merged = list(primary)
    for e in secondary:
        if e["type"] == "var" and e["key"] not in primary_keys:
            merged.append(e)
    # Re-number lines
    for i, e in enumerate(merged, 1):
        e["line"] = i
    return merged


def diff_envs(a: List[Dict], b: List[Dict]) -> List[Dict]:
    """Diff two .env files."""
    vars_a = {e["key"]: e.get("value", "") for e in a if e["type"] == "var"}
    vars_b = {e["key"]: e.get("value", "") for e in b if e["type"] == "var"}
    all_keys = set(vars_a) | set(vars_b)
    diffs = []
    for key in sorted(all_keys):
        if key not in vars_a:
            diffs.append({"type": "added", "key": key, "value": vars_b[key]})
        elif key not in vars_b:
            diffs.append({"type": "removed", "key": key, "value": vars_a[key]})
        elif vars_a[key] != vars_b[key]:
            diffs.append({"type": "changed", "key": key, "old": vars_a[key], "new": vars_b[key]})
    return diffs


def format_env(entries: List[Dict], sort: bool = False) -> str:
    """Format entries back to .env content."""
    lines = []
    if sort:
        vars_entries = [e for e in entries if e["type"] == "var"]
        other_entries = [e for e in entries if e["type"] != "var"]
        vars_entries.sort(key=lambda e: e["key"])
        entries = vars_entries + other_entries

    for e in entries:
        if e["type"] == "comment":
            lines.append(e["raw"])
        elif e["type"] == "blank":
            lines.append("")
        elif e["type"] == "var":
            key = e["key"]
            val = e.get("value", "")
            prefix = "export " if e.get("export") else ""
            if e.get("quoted") and e.get("quote_char"):
                lines.append(f"{prefix}{key}={e['quote_char']}{val}{e['quote_char']}")
            elif " " in val or "#" in val or "'" in val:
                lines.append(f'{prefix}{key}="{val}"')
            else:
                lines.append(f"{prefix}{key}={val}")
    return "\n".join(lines)
