#!/usr/bin/env python3
"""Generate or verify the Architecture Decision Records index (adr/README.md)."""

from __future__ import annotations

import argparse
import dataclasses
import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
ADR_DIR = REPO_ROOT / "adr"
ADR_FILENAME_RE = re.compile(r"^(\d{4})-(.+)\.md$")
TITLE_RE = re.compile(r"^#\s+(?:\d{4}\s*[:\-]\s*)?(.+?)\s*$")
STATUS_RE = re.compile(r"^-\s+Status:\s*(.+?)\s*$", re.IGNORECASE)
DATE_RE = re.compile(r"^-\s+Date:\s*(.+?)\s*$", re.IGNORECASE)


@dataclasses.dataclass(frozen=True)
class AdrEntry:
    adr_id: str
    filename: str
    title: str
    status: str
    date: str


def parse_adr(path: pathlib.Path) -> AdrEntry:
    match = ADR_FILENAME_RE.match(path.name)
    if not match:
        raise ValueError(f"Not a numbered ADR filename: {path.name}")
    adr_id = match.group(1)
    title = match.group(2).replace("-", " ").strip().capitalize()
    status = "unknown"
    date = "unknown"

    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# ") and title == match.group(2).replace("-", " ").strip().capitalize():
            t_match = TITLE_RE.match(line)
            if t_match:
                title = t_match.group(1).strip()
        elif status == "unknown":
            s_match = STATUS_RE.match(line)
            if s_match:
                status = s_match.group(1).strip()
        if date == "unknown":
            d_match = DATE_RE.match(line)
            if d_match:
                date = d_match.group(1).strip()

    return AdrEntry(
        adr_id=adr_id,
        filename=path.name,
        title=title,
        status=status,
        date=date,
    )


def collect_adrs(adr_dir: pathlib.Path) -> list[AdrEntry]:
    entries: list[AdrEntry] = []
    if not adr_dir.exists():
        return entries
    for path in sorted(adr_dir.iterdir()):
        if path.is_file() and ADR_FILENAME_RE.match(path.name):
            entries.append(parse_adr(path))
    return entries


def render_index(entries: list[AdrEntry]) -> str:
    lines = [
        "# Architecture Decision Records",
        "",
        "Architecture decision records (ADRs) for designing Microsoft Sentinel, the Microsoft Sentinel data lake and Microsoft Defender XDR in Australian PROTECTED environments.",
        "",
        "This repository uses the [MADR](https://adr.github.io/madr/) format. Copy [template.md](template.md) when adding a new ADR, then run `python3 scripts/generate_adr_index.py` to update this index.",
        "",
        "<!-- BEGIN GENERATED ADR INDEX -->",
        "",
        "## Index",
        "",
    ]
    if not entries:
        lines.append("No numbered ADRs have been published yet.")
    else:
        lines.append("| ID | Title | Status | Date |")
        lines.append("| :--- | :--- | :--- | :--- |")
        for entry in entries:
            safe_title = entry.title.replace("|", "\\|")
            lines.append(
                f"| ADR-{entry.adr_id} | [{safe_title}]({entry.filename}) | {entry.status} | {entry.date} |"
            )
    lines.extend(
        [
            "",
            "<!-- END GENERATED ADR INDEX -->",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate or verify adr/README.md.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero if adr/README.md is not up to date.",
    )
    parser.add_argument(
        "--adr-dir",
        type=pathlib.Path,
        default=ADR_DIR,
        help="Directory containing ADR markdown files.",
    )
    args = parser.parse_args(argv)

    entries = collect_adrs(args.adr_dir)
    expected = render_index(entries)
    index_path = args.adr_dir / "README.md"

    if args.check:
        if not index_path.exists():
            print(f"ERROR: {index_path} does not exist. Run scripts/generate_adr_index.py.", file=sys.stderr)
            return 1
        actual = index_path.read_text(encoding="utf-8")
        if actual != expected:
            print(
                "ERROR: adr/README.md is out of date. Run `python3 scripts/generate_adr_index.py` and commit the result.",
                file=sys.stderr,
            )
            return 1
        print(f"ADR index check passed ({len(entries)} ADR(s) indexed).")
        return 0

    index_path.write_text(expected, encoding="utf-8")
    print(f"Generated {index_path} ({len(entries)} ADR(s) indexed).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
