from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from agentic_repo_kit.operations import bootstrap, check


CONFIG = """\
kit_version = 1
profiles = ["core"]

[project]
name = "Operator projection fixture"
kind = "test"
roadmap = "ROADMAP.md"
"""


class OperatorProjectionPolicyTests(unittest.TestCase):
    def make_repo(self) -> tuple[tempfile.TemporaryDirectory, Path]:
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        (root / ".agentic-repo.toml").write_text(CONFIG, encoding="utf-8")
        (root / "ROADMAP.md").write_text("# Roadmap\n", encoding="utf-8")
        return temp, root

    def test_generated_contract_defines_operator_projection_boundary(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        bootstrap(root, root / ".agentic-repo.toml")

        agents = (root / "AGENTS.md").read_text(encoding="utf-8")
        playbook = (root / "docs/agent-playbook.md").read_text(encoding="utf-8")
        roadmap_authoring = (root / "docs/roadmap-authoring.md").read_text(encoding="utf-8")

        self.assertIn("derived projection of the roadmap, never as a second source of truth", agents)
        self.assertIn("ready/current `LOCAL ONLY` work", agents)
        self.assertIn("Completed items, blocked downstream items, and purely cloud-executable items", agents)
        self.assertIn("Do not assume a file is named `NEXT-STEPS.md`", agents)
        self.assertIn("reconcile any maintained operator-facing derived projection too", playbook)
        self.assertIn("Project only current human actions", roadmap_authoring)
        self.assertIn("cannot be assumed to semantically derive or prove the correctness", roadmap_authoring)
        self.assertTrue(check(root, root / ".agentic-repo.toml").ok)

    def test_check_does_not_claim_semantic_validation_without_projection_contract(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        bootstrap(root, root / ".agentic-repo.toml")
        (root / "NEXT-STEPS.md").write_text(
            "# Operator checklist\n\n- [ ] deliberately stale fixture text\n",
            encoding="utf-8",
        )

        result = check(root, root / ".agentic-repo.toml")
        self.assertTrue(result.ok, result.problems)


if __name__ == "__main__":
    unittest.main()
