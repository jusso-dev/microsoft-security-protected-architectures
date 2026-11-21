"""Unit tests for repository style, KQL and Mermaid validators."""

from __future__ import annotations

import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

import check_kql
import check_mermaid
import check_style


class StyleCheckTests(unittest.TestCase):
    def test_clean_text_passes(self) -> None:
        text = (
            "# Example\n\n"
            "Plain Australian English for organisations using Microsoft Sentinel.\n"
            "This project is not produced, endorsed or supported by ASD or Microsoft.\n"
        )
        self.assertEqual(check_style.check_text(text, "example.md"), [])

    def test_detects_em_dash(self) -> None:
        text = "Avoid this punctuation \u2014 use commas or colons instead.\n"
        errors = check_style.check_text(text, "example.md")
        self.assertTrue(any("em dash" in err for err in errors))

    def test_detects_emoji(self) -> None:
        text = "No emojis allowed \U0001F680 in docs.\n"
        errors = check_style.check_text(text, "example.md")
        self.assertTrue(any("emoji" in err for err in errors))

    def test_detects_secret_pattern(self) -> None:
        fake_key = "AccountKey=" + ("A" * 32)
        errors = check_style.check_text(fake_key, "config.txt")
        self.assertTrue(any("secret" in err for err in errors))

    def test_detects_endorsement_claim(self) -> None:
        text = "This design is officially endorsed by ASD.\n"
        errors = check_style.check_text(text, "example.md")
        self.assertTrue(any("endorsement" in err for err in errors))


class KqlCheckTests(unittest.TestCase):
    def test_valid_kql_passes(self) -> None:
        query = (
            "// Count recent sign-in events\n"
            "SigninLogs\n"
            "| where TimeGenerated > ago(24h)\n"
            "| summarize Total = count() by ResultType\n"
        )
        self.assertEqual(check_kql.validate_kql(query), [])

    def test_unbalanced_paren_fails(self) -> None:
        query = "SecurityEvent | where EventID in (4624, 4625\n"
        errors = check_kql.validate_kql(query)
        self.assertTrue(any("unclosed '('" in err for err in errors))

    def test_trailing_pipe_fails(self) -> None:
        query = "SecurityEvent |\n"
        errors = check_kql.validate_kql(query)
        self.assertTrue(any("trailing pipe" in err for err in errors))


class MermaidCheckTests(unittest.TestCase):
    def test_extracts_and_validates_flowchart(self) -> None:
        md = (
            "# Diagram\n\n"
            "```mermaid\n"
            "flowchart LR\n"
            "  A[Log Source] --> B[Microsoft Sentinel]\n"
            "```\n"
        )
        blocks = check_mermaid.extract_mermaid_blocks(md)
        self.assertEqual(len(blocks), 1)
        self.assertEqual(check_mermaid.validate_mermaid_syntax(blocks[0][1]), [])

    def test_rejects_unknown_header(self) -> None:
        errors = check_mermaid.validate_mermaid_syntax("notADiagram\n  A --> B\n")
        self.assertTrue(any("unrecognised" in err for err in errors))


if __name__ == "__main__":
    unittest.main()
