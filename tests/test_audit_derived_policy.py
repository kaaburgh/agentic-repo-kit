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
BOTH_CONFIG = CORE_CONFIG.replace(
    'profiles = ["core"]', 'profiles = ["core", "reverse-engineering", "proprietary-target"]'
)
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
        self.assertIn("A retention window is not a record", agents)
        self.assertIn("already-tooled question whose previous result is still unrecorded", pr)
        self.assertTrue(check(root, root / ".agentic-repo.toml").ok)

    def test_durable_result_rule_does_not_collide_with_proprietary_material_policy(self) -> None:
        root = self.make_repo(BOTH_CONFIG)
        agents = (root / "AGENTS.md").read_text(encoding="utf-8")

        self.assertIn("Do not commit proprietary executables/assets, private dumps", agents)
        self.assertIn("must become durable rather than expire with a", agents)
        self.assertIn("commit the safe derived artifact", agents)
        self.assertIn("may not be committed under the repository's other rules", agents)
        self.assertIn("commit its digest plus the reference", agents)
        self.assertNotIn("commit that output rather than", agents)
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

    def test_consecutive_count_declares_its_source_persistence_and_unknown(self) -> None:
        root = self.make_repo(CYCLE_CONFIG)
        cycle = (root / "docs/agent-cycle-run.md").read_text(encoding="utf-8")

        # A count with no named source is the failure this rule exists to avoid:
        # a stateless scheduler reports 1 every cycle and satisfies the contract.
        self.assertIn("stateless scheduler will correctly report `1` every time", cycle)
        self.assertIn("owning item's durable state in the repository", cycle)
        self.assertIn("external runner record the repository explicitly trusts", cycle)
        self.assertIn("report `unknown`", cycle)
        self.assertIn("is not the same as zero", cycle)
        self.assertIn("write this cycle's outcome back to that same durable record", cycle)
        # Start-of-cycle must read the predecessor, not only the report write it.
        self.assertIn("Resolve the previous cycle outcome for the item", cycle)
        self.assertIn("rather than assuming there was no previous cycle", cycle)
        # The contract states its own enforcement boundary, per ARK22.
        self.assertIn("not something the repository contract check verifies", cycle)
        self.assertTrue(check(root, root / ".agentic-repo.toml").ok)

    def test_cycle_outcome_section_is_scoped_to_the_unattended_profile(self) -> None:
        root = self.make_repo(CORE_CONFIG)
        self.assertFalse((root / "docs/agent-cycle-run.md").exists())


if __name__ == "__main__":
    unittest.main()
