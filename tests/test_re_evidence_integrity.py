from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from agentic_repo_kit.operations import bootstrap, check


CONFIG = '''\
kit_version = 1
profiles = ["core", "reverse-engineering", "native-binary-patching"]

[project]
name = "RE evidence fixture"
kind = "reverse-engineering test"
roadmap = "ROADMAP.md"
'''


class ReverseEngineeringEvidenceIntegrityTests(unittest.TestCase):
    def make_repo(self) -> tuple[tempfile.TemporaryDirectory, Path]:
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        (root / ".agentic-repo.toml").write_text(CONFIG, encoding="utf-8")
        (root / "ROADMAP.md").write_text("# Roadmap\n", encoding="utf-8")
        bootstrap(root, root / ".agentic-repo.toml")
        return temp, root

    def test_generated_contract_requires_independent_validation(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        agents = (root / "AGENTS.md").read_text(encoding="utf-8")
        playbook = (root / "docs/agent-playbook.md").read_text(encoding="utf-8")

        self.assertIn("Validation evidence must be independent", agents)
        self.assertIn("internal consistency", agents)
        self.assertIn("what could make the check fail independently", playbook)
        self.assertIn("self-round-trip", playbook)

    def test_generated_contract_preserves_artifact_provenance_and_ambiguity(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        agents = (root / "AGENTS.md").read_text(encoding="utf-8")
        playbook = (root / "docs/agent-playbook.md").read_text(encoding="utf-8")

        self.assertIn("schema/version identifier", agents)
        self.assertIn("reject stale or semantically incompatible evidence", agents)
        self.assertIn("explicit ambiguous/unmapped result", agents)
        self.assertIn("reject missing, legacy, or incompatible provenance", playbook)
        self.assertIn("unmapped`/`ambiguous` outcomes", playbook)

    def test_generated_contract_requires_observed_abi_evidence(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        agents = (root / "AGENTS.md").read_text(encoding="utf-8")
        pr = (root / ".github/pull_request_template.md").read_text(encoding="utf-8")

        self.assertIn("Treat ABI and calling convention as target evidence", agents)
        self.assertIn("Do not choose a hook/trampoline ABI solely", agents)
        self.assertIn("ABI/calling-convention claims", pr)

    def test_experiment_template_requests_reproducible_discriminating_record(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        experiments = (root / "docs/experiments/README.md").read_text(encoding="utf-8")

        self.assertIn("expected differentiating outcomes", experiments)
        self.assertIn("bounded artifact names", experiments)
        self.assertIn("next question", experiments)
        self.assertIn("what makes the validation independent", experiments)

    def test_fixture_contract_remains_self_consistent(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        self.assertTrue(check(root, root / ".agentic-repo.toml").ok)


if __name__ == "__main__":
    unittest.main()
