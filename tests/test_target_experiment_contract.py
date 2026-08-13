from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from agentic_repo_kit.operations import bootstrap, check


CONFIG = '''\
kit_version = 1
profiles = ["core", "reverse-engineering", "proprietary-target", "graphics"]

[project]
name = "Target experiment fixture"
kind = "runtime reverse-engineering test"
roadmap = "ROADMAP.md"
'''

PROPRIETARY_ONLY_CONFIG = '''\
kit_version = 1
profiles = ["core", "proprietary-target"]

[project]
name = "Proprietary target fixture"
kind = "proprietary runtime test"
roadmap = "ROADMAP.md"
'''


class TargetExperimentContractTests(unittest.TestCase):
    def make_repo(self, config: str = CONFIG) -> tuple[tempfile.TemporaryDirectory, Path]:
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        (root / ".agentic-repo.toml").write_text(config, encoding="utf-8")
        (root / "ROADMAP.md").write_text("# Roadmap\n", encoding="utf-8")
        bootstrap(root, root / ".agentic-repo.toml")
        return temp, root

    def test_runtime_contract_requires_semantic_oracle_and_bounds(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        agents = (root / "AGENTS.md").read_text(encoding="utf-8")
        playbook = (root / "docs/agent-playbook.md").read_text(encoding="utf-8")

        self.assertIn("oracle that directly distinguishes the claimed target state or behavior", agents)
        self.assertIn("Declare termination/liveness expectations", agents)
        self.assertIn("State the success and failure oracles before the run", playbook)
        self.assertIn("Bound waits, retries, action counts, captures, log volume, and total runtime", playbook)

    def test_control_capability_is_separate_from_target_evidence(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        agents = (root / "AGENTS.md").read_text(encoding="utf-8")
        playbook = (root / "docs/agent-playbook.md").read_text(encoding="utf-8")
        pr = (root / ".github/pull_request_template.md").read_text(encoding="utf-8")

        self.assertIn("Keep harness capability separate from target-specific evidence", agents)
        self.assertIn("Record that as capability evidence", playbook)
        self.assertIn("Harness/control capability evidence is not presented as target-specific runtime evidence", pr)

    def test_proprietary_inputs_are_immutable_and_artifacts_sanitized(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        agents = (root / "AGENTS.md").read_text(encoding="utf-8")
        playbook = (root / "docs/agent-playbook.md").read_text(encoding="utf-8")
        pr = (root / ".github/pull_request_template.md").read_text(encoding="utf-8")

        self.assertIn("immutable evidence inputs", agents)
        self.assertIn("verified copy, isolated work directory, overlay", agents)
        self.assertIn("Sanitize private host paths", agents)
        self.assertIn("leave the supplied source evidence untouched", playbook)
        self.assertIn("without embedding proprietary payloads", pr)

    def test_run_record_has_replayable_detached_provenance(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        agents = (root / "AGENTS.md").read_text(encoding="utf-8")
        playbook = (root / "docs/agent-playbook.md").read_text(encoding="utf-8")

        self.assertIn("detached machine-readable run record", agents)
        self.assertIn("scenario/config identity", agents)
        self.assertIn("semantic oracle results", agents)
        self.assertIn("detached machine-readable run record", playbook)
        self.assertIn("names/digests of bounded artifacts", playbook)

    def test_proprietary_profile_stands_alone_with_versioned_run_manifest(self) -> None:
        temp, root = self.make_repo(PROPRIETARY_ONLY_CONFIG)
        self.addCleanup(temp.cleanup)
        agents = (root / "AGENTS.md").read_text(encoding="utf-8")
        playbook = (root / "docs/agent-playbook.md").read_text(encoding="utf-8")
        pr = (root / ".github/pull_request_template.md").read_text(encoding="utf-8")

        self.assertIn("explicit schema/version", agents)
        self.assertIn("explicit schema/version", playbook)
        self.assertIn("reject an unsupported manifest schema", playbook)
        self.assertIn("explicit supported schema/version", pr)
        self.assertTrue(check(root, root / ".agentic-repo.toml").ok)

    def test_graphics_oracle_is_checkpoint_specific(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        agents = (root / "AGENTS.md").read_text(encoding="utf-8")

        self.assertIn("acceptance oracle must prove the intended checkpoint or graphics state", agents)
        self.assertIn("changed frame/hash", agents)
        self.assertIn("checkpoint-specific regions", agents)

    def test_fixture_contract_remains_consistent(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        self.assertTrue(check(root, root / ".agentic-repo.toml").ok)


if __name__ == "__main__":
    unittest.main()
