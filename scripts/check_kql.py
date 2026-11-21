#!/usr/bin/env python3
"""Lightweight structural validation for KQL files and fenced kql code blocks."""

from __future__ import annotations

import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
IGNORED_DIRS = {".git", "node_modules", ".terraform", ".venv", "__pycache__"}
KQL_BLOCK_RE = re.compile(
    r"(?m)^[ \t]*(`{3,}|~{3,})kql[ \t]*\r?\n(.*?)\r?\n^[ \t]*\1[ \t]*$",
    re.DOTALL | re.IGNORECASE,
)


def _strip_comments_and_strings(query: str) -> tuple[str, list[str]]:
    """Return query with comments/string contents masked and any quote errors."""
    errors: list[str] = []
    out: list[str] = []
    i = 0
    n = len(query)
    while i < n:
        ch = query[i]
        # Line comment //
        if ch == "/" and i + 1 < n and query[i + 1] == "/":
            while i < n and query[i] != "\n":
                i += 1
            continue
        # Multi-line string literal ```...``` or ~~~...~~~
        if query[i : i + 3] in ("```", "~~~"):
            delim = query[i : i + 3]
            end = query.find(delim, i + 3)
            if end == -1:
                errors.append(f"unterminated multi-line string literal ({delim})")
                break
            out.append(" ")
            i = end + 3
            continue
        # Verbatim string @"..." or @'...'
        if ch == "@" and i + 1 < n and query[i + 1] in ('"', "'"):
            quote = query[i + 1]
            i += 2
            closed = False
            while i < n:
                if query[i] == quote:
                    if i + 1 < n and query[i + 1] == quote:
                        i += 2
                        continue
                    closed = True
                    i += 1
                    break
                i += 1
            if not closed:
                errors.append(f"unterminated verbatim string ({quote})")
            out.append(" ")
            continue
        # Regular string "..." or '...'
        if ch in ('"', "'"):
            quote = ch
            i += 1
            closed = False
            while i < n:
                if query[i] == "\\" and i + 1 < n:
                    i += 2
                    continue
                if query[i] == quote:
                    closed = True
                    i += 1
                    break
                if query[i] == "\n":
                    break
                i += 1
            if not closed:
                errors.append(f"unterminated string literal ({quote})")
            out.append(" ")
            continue
        out.append(ch)
        i += 1
    return "".join(out), errors


def validate_kql(query: str) -> list[str]:
    errors: list[str] = []
    if not query.strip():
        return ["empty KQL query"]

    masked, quote_errors = _strip_comments_and_strings(query)
    errors.extend(quote_errors)

    stack: list[str] = []
    pairs = {")": "(", "]": "[", "}": "{"}
    for ch in masked:
        if ch in "([{":
            stack.append(ch)
        elif ch in ")]}":
            if not stack or stack[-1] != pairs[ch]:
                errors.append(f"unmatched closing '{ch}'")
            else:
                stack.pop()
    for unclosed in stack:
        errors.append(f"unclosed '{unclosed}'")

    non_empty_lines = [line.strip() for line in masked.splitlines() if line.strip()]
    if not non_empty_lines:
        errors.append("query contains only comments")
    elif non_empty_lines[-1].endswith("|"):
        errors.append("query ends with a trailing pipe operator '|'")

    return errors


def check_repo(root: pathlib.Path = REPO_ROOT) -> tuple[int, list[str]]:
    errors: list[str] = []
    blocks_checked = 0
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if any(part in IGNORED_DIRS for part in rel.parts):
            continue
        if path.suffix.lower() == ".kql":
            blocks_checked += 1
            for err in validate_kql(path.read_text(encoding="utf-8")):
                errors.append(f"{rel}: {err}")
        elif path.suffix.lower() == ".md":
            content = path.read_text(encoding="utf-8")
            for idx, match in enumerate(KQL_BLOCK_RE.finditer(content), start=1):
                blocks_checked += 1
                for err in validate_kql(match.group(2)):
                    errors.append(f"{rel} (kql block #{idx}): {err}")
    return blocks_checked, errors


def main() -> int:
    count, errors = check_repo(REPO_ROOT)
    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        return 1
    print(f"KQL check passed ({count} block(s) validated).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
