from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from agentic_repo_kit.operations import bootstrap


CONFIG = """\
kit_version = 1
profiles = ["core"]

[project]
name = "Playbook fixture"
kind = "test"
roadmap = "ROADMAP.md"
"""


class PlaybookGuardrailTests(unittest.TestCase):
    def render_playbook(self) -> str:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        (root / ".agentic-repo.toml").write_text(CONFIG, encoding="utf-8")
        (root / "ROADMAP.md").write_text("# Roadmap\n", encoding="utf-8")
        bootstrap(root, root / ".agentic-repo.toml")
        return (root / "docs/agent-playbook.md").read_text(encoding="utf-8")

    def test_process_only_pr_exception_is_explicit(self) -> None:
        playbook = self.render_playbook()
        self.assertIn(
            "a process-only PR may omit a roadmap item when it explicitly explains why no roadmap item applies",
            playbook,
        )
        self.assertIn(
            "for a process-only change, explicitly establish that no roadmap item applies instead of inventing one",
            playbook,
        )
        self.assertIn("For process-only work", playbook)

    def test_history_inspection_respects_active_evidence_policy(self) -> None:
        playbook = self.render_playbook()
        self.assertIn("only history permitted by the active evidence policy", playbook)
        self.assertIn(
            "If a blind-research gate excludes unsupported history, do not inspect excluded commits, branches, deleted material, or abandoned work for target-specific investigation.",
            playbook,
        )


if __name__ == "__main__":
    unittest.main()
