from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from agentic_repo_kit.operations import bootstrap, check


CORE_CONFIG = '''\
kit_version = 1
profiles = ["core"]

[project]
name = "Audit policy fixture"
kind = "test"
roadmap = "ROADMAP.md"
'''

RE_CONFIG = CORE_CONFIG.replace('profiles = ["core"]', 'profiles = ["core", "reverse-engineering"]')
CYCLE_CONFIG = CORE_CONFIG.replace('profiles = ["core"]', 'profiles = ["core", "unattended-agent-cycle"]')


class AuditDerivedPolicyTests(unittest.TestCase):
    def make_repo(self, config: str) -> Path:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        (root / ".agentic-repo.toml").write_text(config, encoding="utf-8")
        (root / "ROADMAP.md").write_text("# Roadmap\n", encoding="utf-8")
        bootstrap(root, root / ".agentic-repo.toml")
        return root

    def test_core_contract_rejects_self_declared_enforcement(self) -> None:
        root = self.make_repo(CORE_CONFIG)
        agents = (root / "AGENTS.md").read_text(encoding="utf-8")
        pr = (root / ".github/pull_request_template.md").read_text(encoding="utf-8")

        self.assertIn("enforced by a property of the data", agents)
        self.assertIn("declares its own compliance", agents)
        self.assertIn("reports conformance that was never checked", agents)
        self.assertIn("only be judged by a person", agents)
        self.assertIn("not against a self-declared label", pr)
        self.assertTrue(check(root, root / ".agentic-repo.toml").ok)

    def test_reverse_engineering_contract_blocks_retooling_an_open_question(self) -> None:
        root = self.make_repo(RE_CONFIG)
        agents = (root / "AGENTS.md").read_text(encoding="utf-8")
        pr = (root / ".github/pull_request_template.md").read_text(encoding="utf-8")

        self.assertIn("second producer for a question the repository is already tooled for", agents)
        self.assertIn("evidence gap into a tooling backlog", agents)
        self.assertIn("visible only across the sequence", agents)
        self.assertIn("expiring CI artifact", agents)
        self.assertIn("already-tooled question whose previous result is still unrecorded", pr)
        self.assertTrue(check(root, root / ".agentic-repo.toml").ok)

    def test_core_only_repository_does_not_receive_the_reverse_engineering_rule(self) -> None:
        root = self.make_repo(CORE_CONFIG)
        agents = (root / "AGENTS.md").read_text(encoding="utf-8")
        self.assertNotIn("second producer for a question", agents)

    def test_unattended_cycle_report_classifies_its_outcome(self) -> None:
        root = self.make_repo(CYCLE_CONFIG)
        cycle = (root / "docs/agent-cycle-run.md").read_text(encoding="utf-8")

        self.assertIn("## Cycle outcome", cycle)
        self.assertIn("`tooling only`", cycle)
        self.assertIn("Tooling is a legitimate outcome", cycle)
        self.assertIn("consecutive cycles have now ended that way", cycle)
        self.assertIn("cycle outcome for the selected item", cycle)
        self.assertTrue(check(root, root / ".agentic-repo.toml").ok)

    def test_cycle_outcome_section_is_scoped_to_the_unattended_profile(self) -> None:
        root = self.make_repo(CORE_CONFIG)
        self.assertFalse((root / "docs/agent-cycle-run.md").exists())


if __name__ == "__main__":
    unittest.main()
