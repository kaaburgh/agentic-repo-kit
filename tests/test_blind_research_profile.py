from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from agentic_repo_kit.operations import bootstrap, check
from agentic_repo_kit.profiles import available_profiles


CONFIG = '''\
kit_version = 1
profiles = ["core", "reverse-engineering", "blind-research"]

[project]
name = "Blind research fixture"
kind = "closed-target research test"
roadmap = "ROADMAP.md"
'''


class BlindResearchProfileTests(unittest.TestCase):
    def make_repo(self) -> tuple[tempfile.TemporaryDirectory, Path]:
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        (root / ".agentic-repo.toml").write_text(CONFIG, encoding="utf-8")
        (root / "ROADMAP.md").write_text("# Roadmap\n", encoding="utf-8")
        bootstrap(root, root / ".agentic-repo.toml")
        return temp, root

    def test_profile_is_discoverable_and_opt_in(self) -> None:
        self.assertIn("blind-research", available_profiles())
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        lock = (root / ".agentic-repo.lock.json").read_text(encoding="utf-8")
        self.assertIn('"blind-research"', lock)

    def test_gate_is_project_defined_not_hardcoded_to_a_milestone(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        agents = (root / "AGENTS.md").read_text(encoding="utf-8")
        playbook = (root / "docs/agent-playbook.md").read_text(encoding="utf-8")

        self.assertIn("project must define the gate boundary", agents)
        self.assertIn("does not invent a milestone name", agents)
        self.assertIn("project-local blind-research gate definition", playbook)
        self.assertIn("provenance experiment itself is underspecified", playbook)

    def test_provenance_is_separate_from_evidence_class(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        agents = (root / "AGENTS.md").read_text(encoding="utf-8")
        pr = (root / ".github/pull_request_template.md").read_text(encoding="utf-8")

        self.assertIn("separate dimension from evidence class", agents)
        self.assertIn("`clean`, `contaminated`, and `external-assisted`", agents)
        self.assertIn("separately from evidence class", pr)

    def test_contamination_cannot_be_reversed_by_corroboration(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        agents = (root / "AGENTS.md").read_text(encoding="utf-8")
        playbook = (root / "docs/agent-playbook.md").read_text(encoding="utf-8")

        self.assertIn("does not restore blindness", agents)
        self.assertIn("without relabeling them `clean`", playbook)

    def test_rescue_requires_blocker_and_durable_bounded_unlock(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        agents = (root / "AGENTS.md").read_text(encoding="utf-8")
        pr = (root / ".github/pull_request_template.md").read_text(encoding="utf-8")

        self.assertIn("First record a concrete blocker or negative result", agents)
        self.assertIn("explicit maintainer decision recorded durably", agents)
        self.assertIn("exception does not generalize", agents)
        self.assertIn("prior durable blocker/negative result", pr)

    def test_post_blind_comparison_preserves_independent_record(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        agents = (root / "AGENTS.md").read_text(encoding="utf-8")
        playbook = (root / "docs/agent-playbook.md").read_text(encoding="utf-8")

        self.assertIn("Preserve the independent result first", agents)
        self.assertIn("reports agreements, disagreements, missed structures, and false positives", playbook)

    def test_operator_artifacts_do_not_bypass_recovered_knowledge_gate(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        playbook = (root / "docs/agent-playbook.md").read_text(encoding="utf-8")
        self.assertIn("operator-provided tools or artifacts", playbook)
        self.assertIn("target-specific recovered addresses, symbols, structures, pseudocode", playbook)
        self.assertTrue(check(root, root / ".agentic-repo.toml").ok)


if __name__ == "__main__":
    unittest.main()
