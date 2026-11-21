#!/usr/bin/env python3
"""Repository style, secret hygiene and endorsement claim checks."""

from __future__ import annotations

import pathlib
import re
import sys
from typing import Iterable

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent

CHECKED_EXTENSIONS = {
    ".md",
    ".bicep",
    ".bicepparam",
    ".tf",
    ".tfvars",
    ".yml",
    ".yaml",
    ".json",
    ".jsonc",
    ".py",
    ".sh",
    ".kql",
    ".toml",
}

IGNORED_DIRS = {
    ".git",
    "node_modules",
    ".terraform",
    ".venv",
    "__pycache__",
    "dist",
    "bin",
    "obj",
}

EM_DASH = "\u2014"

# Common Unicode emoji ranges and selectors.
EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001F5FF"  # Misc Symbols and Pictographs
    "\U0001F600-\U0001F64F"  # Emoticons
    "\U0001F680-\U0001F6FF"  # Transport and Map
    "\U0001F700-\U0001F77F"  # Alchemical Symbols
    "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
    "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
    "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
    "\U0001FA00-\U0001FAFF"  # Chess / Symbols and Pictographs Extended-A
    "\u2600-\u26FF"          # Misc symbols
    "\u2700-\u27BF"          # Dingbats
    "\uFE0F"                 # Variation Selector-16
    "\u20E3"                 # Combining Enclosing Keycap
    "]"
)

SECRET_PATTERNS = [
    ("Private key block", re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")),
    ("Azure storage account key", re.compile(r"AccountKey=[A-Za-z0-9+/=]{20,}")),
    ("SharedAccessKey secret", re.compile(r"SharedAccessKey=[A-Za-z0-9+/=]{20,}")),
    ("GitHub token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}\b")),
    ("GitHub fine-grained token", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b")),
]

ENDORSEMENT_RE = re.compile(
    r"(?i)\b(?:officially\s+)?(?:endorsed|approved|certified)\s+"
    r"(?:(?:or|and)\s+(?:supported|approved|endorsed|certified)\s+)*"
    r"by\s+(?:the\s+)?(?:ASD|ACSC|Microsoft)\b"
)

NEGATION_BEFORE_ENDORSEMENT_RE = re.compile(
    r"(?i)(?:\b(?:not|no|never|neither|nor|without)\b|"
    r"\b(?:do\s+not|does\s+not|cannot|no\s+claim\s+of)\b)"
    r"[^.;:!?]{0,60}$"
)


def iter_repo_files(root: pathlib.Path) -> Iterable[pathlib.Path]:
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if any(part in IGNORED_DIRS for part in path.relative_to(root).parts):
            continue
        if path.suffix.lower() in CHECKED_EXTENSIONS:
            yield path


def check_text(text: str, filename: str = "<input>") -> list[str]:
    errors: list[str] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        if EM_DASH in line:
            errors.append(
                f"{filename}:{line_no}: em dash character (U+2014) is not permitted"
            )
        emoji_match = EMOJI_RE.search(line)
        if emoji_match:
            codepoint = f"U+{ord(emoji_match.group(0)):04X}"
            errors.append(
                f"{filename}:{line_no}: emoji or symbol character ({codepoint}) is not permitted"
            )
        for label, pattern in SECRET_PATTERNS:
            if pattern.search(line):
                errors.append(
                    f"{filename}:{line_no}: potential secret detected ({label})"
                )
        if filename.endswith(".md"):
            for match in ENDORSEMENT_RE.finditer(line):
                prefix = line[: match.start()]
                if not NEGATION_BEFORE_ENDORSEMENT_RE.search(prefix):
                    errors.append(
                        f"{filename}:{line_no}: possible ASD, ACSC or Microsoft endorsement claim"
                    )
    return errors


def check_file(path: pathlib.Path, root: pathlib.Path = REPO_ROOT) -> list[str]:
    rel = str(path.relative_to(root)) if path.is_relative_to(root) else str(path)
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        return [f"{rel}: unable to decode as UTF-8 ({exc})"]
    return check_text(content, rel)


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    paths = [pathlib.Path(arg).resolve() for arg in args] if args else list(iter_repo_files(REPO_ROOT))
    all_errors: list[str] = []
    for path in paths:
        all_errors.extend(check_file(path))
    if all_errors:
        for err in all_errors:
            print(f"ERROR: {err}", file=sys.stderr)
        print(f"Style check failed with {len(all_errors)} issue(s).", file=sys.stderr)
        return 1
    print(f"Style check passed across {len(paths)} file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
