from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from agentic_repo_kit.operations import bootstrap, check, upgrade


CONFIG = '''\
kit_version = 1
profiles = ["core"]

[project]
name = "Fixture"
kind = "test"
roadmap = "ROADMAP.md"
'''


class OperatorHandoffPolicyTests(unittest.TestCase):
    def make_repo(self) -> tuple[tempfile.TemporaryDirectory, Path]:
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        (root / ".agentic-repo.toml").write_text(CONFIG, encoding="utf-8")
        (root / "ROADMAP.md").write_text("# Roadmap\n", encoding="utf-8")
        return temp, root

    def test_core_contract_includes_operator_handoff_policy(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        bootstrap(root, root / ".agentic-repo.toml")

        agents = (root / "AGENTS.md").read_text(encoding="utf-8")
        playbook = (root / "docs/agent-playbook.md").read_text(encoding="utf-8")
        roadmap_authoring = (root / "docs/roadmap-authoring.md").read_text(encoding="utf-8")
        lock = json.loads((root / ".agentic-repo.lock.json").read_text(encoding="utf-8"))

        self.assertIn("**not** evidence that the capability is unavailable to the project", agents)
        self.assertIn("pause only the line of work", agents)
        self.assertIn("exact missing tool/capability", agents)
        self.assertIn("Do not infer `LOCAL ONLY`", playbook)
        self.assertIn("failed acquisition in one sandbox is not, by itself, evidence for `LOCAL ONLY`", roadmap_authoring)
        self.assertEqual("0.1.1", lock["tool_version"])
        self.assertTrue(check(root, root / ".agentic-repo.toml").ok)

    def test_upgrade_restores_policy_and_preserves_local_input(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        local = root / "local.md"
        local_text = "## Fixture-specific rule\n\nKeep this local input.\n"
        local.write_text(local_text, encoding="utf-8")
        (root / ".agentic-repo.toml").write_text(
            CONFIG + '\n[local]\npolicy_files = ["local.md"]\n',
            encoding="utf-8",
        )
        bootstrap(root, root / ".agentic-repo.toml")

        agents = root / "AGENTS.md"
        agents.write_text(
            agents.read_text(encoding="utf-8").replace(
                "A missing tool or capability in one agent environment is **not** evidence",
                "A stale generated contract is **not** evidence",
            ),
            encoding="utf-8",
        )

        changed = upgrade(root, root / ".agentic-repo.toml")
        self.assertIn("AGENTS.md", changed)
        restored = agents.read_text(encoding="utf-8")
        self.assertIn("A missing tool or capability in one agent environment is **not** evidence", restored)
        self.assertIn("Fixture-specific rule", restored)
        self.assertEqual(local_text, local.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
