"""Unit tests for the MADR ADR index generator."""

from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

import generate_adr_index


class AdrIndexTests(unittest.TestCase):
    def test_empty_directory_renders_placeholder(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            adr_dir = pathlib.Path(tmpdir)
            entries = generate_adr_index.collect_adrs(adr_dir)
            self.assertEqual(entries, [])
            rendered = generate_adr_index.render_index(entries)
            self.assertIn("No numbered ADRs have been published yet.", rendered)

    def test_parses_and_checks_numbered_adrs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            adr_dir = pathlib.Path(tmpdir)
            (adr_dir / "template.md").write_text("# Template\n", encoding="utf-8")
            (adr_dir / "0001-workspace-design.md").write_text(
                "# 0001: Workspace and tenant design\n\n"
                "- Status: accepted\n"
                "- Date: 2026-11-21\n",
                encoding="utf-8",
            )
            rc_gen = generate_adr_index.main(["--adr-dir", str(adr_dir)])
            self.assertEqual(rc_gen, 0)
            readme = (adr_dir / "README.md").read_text(encoding="utf-8")
            self.assertIn("| ADR-0001 | [Workspace and tenant design](0001-workspace-design.md) | accepted | 2026-11-21 |", readme)
            self.assertNotIn("template.md)", readme.split("## Index", 1)[1])

            rc_check = generate_adr_index.main(["--check", "--adr-dir", str(adr_dir)])
            self.assertEqual(rc_check, 0)

            (adr_dir / "README.md").write_text("# Stale\n", encoding="utf-8")
            rc_stale = generate_adr_index.main(["--check", "--adr-dir", str(adr_dir)])
            self.assertEqual(rc_stale, 1)


if __name__ == "__main__":
    unittest.main()
