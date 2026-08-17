from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from agentic_repo_kit.errors import AgenticRepoError
from agentic_repo_kit.operations import bootstrap, check, upgrade
from agentic_repo_kit.profiles import available_profiles


CORE_CONFIG = '''\
kit_version = 1
profiles = ["core"]

[project]
name = "Unattended fixture"
kind = "test"
roadmap = "ROADMAP.md"
'''
UNATTENDED_CONFIG = CORE_CONFIG.replace(
    'profiles = ["core"]',
    'profiles = ["core", "unattended-agent-cycle"]',
)
CYCLE_DOC = "docs/agent-cycle-run.md"


class UnattendedAgentCycleTests(unittest.TestCase):
    def _repo(self, temp: str, config_text: str = CORE_CONFIG) -> tuple[Path, Path]:
        root = Path(temp)
        config = root / ".agentic-repo.toml"
        config.write_text(config_text, encoding="utf-8")
        (root / "ROADMAP.md").write_text("# Roadmap\n", encoding="utf-8")
        return root, config

    def test_profile_is_discoverable_opt_in_and_links_contract(self) -> None:
        self.assertIn("unattended-agent-cycle", available_profiles())

        with tempfile.TemporaryDirectory() as temp:
            root, config = self._repo(temp, UNATTENDED_CONFIG)
            changed = bootstrap(root, config)
            self.assertIn(CYCLE_DOC, changed)
            agents = (root / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("docs/agent-cycle-run.md", agents)
            lock = json.loads((root / ".agentic-repo.lock.json").read_text(encoding="utf-8"))
            self.assertIn(CYCLE_DOC, lock["generated"])
            self.assertTrue(check(root, config).ok)

        with tempfile.TemporaryDirectory() as temp:
            root, config = self._repo(temp, CORE_CONFIG)
            bootstrap(root, config)
            self.assertFalse((root / CYCLE_DOC).exists())
            self.assertNotIn("docs/agent-cycle-run.md", (root / "AGENTS.md").read_text(encoding="utf-8"))
            self.assertTrue(check(root, config).ok)

    def test_check_detects_cycle_contract_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root, config = self._repo(temp, UNATTENDED_CONFIG)
            bootstrap(root, config)
            path = root / CYCLE_DOC
            path.write_text(path.read_text(encoding="utf-8") + "\ndrift\n", encoding="utf-8")

            result = check(root, config)
            self.assertFalse(result.ok)
            self.assertIn(f"generated file drift: {CYCLE_DOC}", result.problems)

    def test_upgrade_from_pre_ark14_lock_adds_contract_transactionally(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root, config = self._repo(temp, CORE_CONFIG)
            bootstrap(root, config)
            before_agents = (root / "AGENTS.md").read_text(encoding="utf-8")

            config.write_text(UNATTENDED_CONFIG, encoding="utf-8")
            changed = upgrade(root, config)

            self.assertIn("AGENTS.md", changed)
            self.assertIn(CYCLE_DOC, changed)
            self.assertNotEqual(before_agents, (root / "AGENTS.md").read_text(encoding="utf-8"))
            self.assertTrue((root / CYCLE_DOC).is_file())
            self.assertTrue(check(root, config).ok)

    def test_upgrade_refuses_unmarked_project_owned_cycle_contract_before_writes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root, config = self._repo(temp, CORE_CONFIG)
            bootstrap(root, config)
            before_agents = (root / "AGENTS.md").read_text(encoding="utf-8")
            before_lock = (root / ".agentic-repo.lock.json").read_text(encoding="utf-8")

            config.write_text(UNATTENDED_CONFIG, encoding="utf-8")
            path = root / CYCLE_DOC
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("project-owned contract\n", encoding="utf-8")

            with self.assertRaisesRegex(AgenticRepoError, "refusing to overwrite unmanaged or drifted file"):
                upgrade(root, config)

            self.assertEqual(before_agents, (root / "AGENTS.md").read_text(encoding="utf-8"))
            self.assertEqual(before_lock, (root / ".agentic-repo.lock.json").read_text(encoding="utf-8"))
            self.assertEqual("project-owned contract\n", path.read_text(encoding="utf-8"))

    def test_cycle_contract_covers_unattended_invariants(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root, config = self._repo(temp, UNATTENDED_CONFIG)
            bootstrap(root, config)
            contract = (root / CYCLE_DOC).read_text(encoding="utf-8")

            for required in (
                "Missing DNS, a missing CLI client, a missing working tree, and a non-first-class host OS",
                "Never assume the branch is named `main`",
                "trusted default-branch head",
                "CYCLE CONTRACT: MISSING (absent on trusted revision <sha>)",
                "If the PR changes or introduces this contract",
                "proposed content under review",
                "the proposed copy cannot self-authorize unattended policy",
                "Path A — atomic Git-object construction",
                "target branch ref is absent",
                "re-confirm absence immediately before ref creation",
                "compare-and-swap failure",
                "expected old SHA",
                "non-force fast-forward/compare-and-swap update",
                "not a Path A failure for fallback purposes",
                "refused or rejected twice in the same run",
                "cannot perform the required atomic object/ref operation",
                "never counts toward this fallback threshold",
                "expected current blob SHA",
                "expected-absence precondition",
                "verify the branch head equals the preceding intermediate commit",
                "verify it equals the final intermediate commit",
                "none — no repository writes",
                "does not require Path A/B details",
                "ATOMICITY: LOST — per-file fallback used",
                "Bind every CI status, review submission, review request, review-thread disposition, reaction, and merge-readiness verdict to one exact commit SHA",
                "do not wait for GitHub review state `APPROVED`",
                "👍 reaction on the PR body",
                "A PR-body reaction has no native commit SHA",
                "reaction was created after the exact current head became the PR head",
                "same-source SHA-bearing approval review/verdict",
                "classify the reaction as `unbound`",
                "Owner-account review submissions are not distinguishable by author identity alone",
                "partially addressed",
                "disputed",
                "Never resolve an unaddressed thread",
                "validation execution level",
                "evidence mechanism",
                "INSTRUCTION DEFECTS",
                "CYCLE CONTRACT",
            ):
                self.assertIn(required, contract)

            self.assertIn("Approval eligibility, override acceptance", contract)
            self.assertIn("remain external", contract)


if __name__ == "__main__":
    unittest.main()
