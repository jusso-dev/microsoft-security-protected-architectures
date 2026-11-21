#!/usr/bin/env python3
"""Extract and validate Mermaid diagrams in Markdown files."""

from __future__ import annotations

import argparse
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
IGNORED_DIRS = {".git", "node_modules", ".terraform", ".venv", "__pycache__"}
MERMAID_BLOCK_RE = re.compile(r"```mermaid\s*\n(.*?)\n```", re.DOTALL)

VALID_HEADERS = (
    "flowchart",
    "graph",
    "sequenceDiagram",
    "classDiagram",
    "stateDiagram",
    "stateDiagram-v2",
    "erDiagram",
    "gantt",
    "pie",
    "journey",
    "gitGraph",
    "mindmap",
    "timeline",
    "C4Context",
    "C4Container",
    "C4Component",
    "C4Dynamic",
    "C4Deployment",
    "xychart-beta",
    "block-beta",
    "architecture-beta",
)


def extract_mermaid_blocks(markdown_text: str) -> list[tuple[int, str]]:
    """Return list of (1-based line number, diagram source) pairs."""
    blocks: list[tuple[int, str]] = []
    for match in MERMAID_BLOCK_RE.finditer(markdown_text):
        line_no = markdown_text.count("\n", 0, match.start()) + 1
        blocks.append((line_no, match.group(1)))
    return blocks


def validate_mermaid_syntax(source: str) -> list[str]:
    """Perform static structural checks on a Mermaid diagram."""
    errors: list[str] = []
    lines = [
        line.strip()
        for line in source.splitlines()
        if line.strip() and not line.strip().startswith("%%")
    ]
    if not lines:
        return ["empty Mermaid diagram"]
    first_line = lines[0]
    if not any(first_line.startswith(header) for header in VALID_HEADERS):
        errors.append(f"unrecognised Mermaid diagram header: {first_line!r}")
    return errors


def render_with_mmdc(
    source: str, mmdc_path: str, puppeteer_config: pathlib.Path | None
) -> str | None:
    """Render a Mermaid diagram using mmdc; return error text on failure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = pathlib.Path(tmpdir)
        in_file = tmp / "diagram.mmd"
        out_file = tmp / "diagram.svg"
        in_file.write_text(source, encoding="utf-8")
        cmd = [mmdc_path, "-i", str(in_file), "-o", str(out_file)]
        if puppeteer_config and puppeteer_config.exists():
            cmd.extend(["-p", str(puppeteer_config)])
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            detail = (result.stderr or result.stdout or "unknown mmdc failure").strip()
            return detail
        if not out_file.exists() or out_file.stat().st_size == 0:
            return "mmdc produced an empty output file"
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Mermaid diagrams in Markdown.")
    parser.add_argument(
        "--syntax-only",
        action="store_true",
        help="Run static header checks without invoking mmdc.",
    )
    parser.add_argument(
        "--mmdc",
        default="mmdc",
        help="Path or command name for mermaid-cli (default: mmdc).",
    )
    args = parser.parse_args(argv)

    mmdc_path = None if args.syntax_only else shutil.which(args.mmdc)
    if not args.syntax_only and not mmdc_path:
        print(
            "ERROR: mmdc not found in PATH. Install @mermaid-js/mermaid-cli or pass --syntax-only.",
            file=sys.stderr,
        )
        return 1

    puppeteer_config = REPO_ROOT / "scripts" / "puppeteer-config.json"
    errors: list[str] = []
    diagram_count = 0

    for path in sorted(REPO_ROOT.rglob("*.md")):
        rel = path.relative_to(REPO_ROOT)
        if any(part in IGNORED_DIRS for part in rel.parts):
            continue
        blocks = extract_mermaid_blocks(path.read_text(encoding="utf-8"))
        for idx, (line_no, source) in enumerate(blocks, start=1):
            diagram_count += 1
            syntax_errors = validate_mermaid_syntax(source)
            for err in syntax_errors:
                errors.append(f"{rel}:{line_no} (diagram #{idx}): {err}")
            if mmdc_path and not syntax_errors:
                render_err = render_with_mmdc(source, mmdc_path, puppeteer_config)
                if render_err:
                    errors.append(
                        f"{rel}:{line_no} (diagram #{idx}): render failed: {render_err}"
                    )

    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        print(f"Mermaid check failed with {len(errors)} error(s).", file=sys.stderr)
        return 1

    mode = "syntax-only" if args.syntax_only else "render"
    print(f"Mermaid check ({mode}) passed across {diagram_count} diagram(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
