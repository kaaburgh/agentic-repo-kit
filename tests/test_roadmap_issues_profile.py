from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from agentic_repo_kit.operations import bootstrap, check, upgrade
from agentic_repo_kit.profiles import available_profiles


CORE_CONFIG = '''\
kit_version = 1
profiles = ["core"]

[project]
name = "Roadmap issue fixture"
kind = "test"
roadmap = "ROADMAP.md"
'''
ISSUES_CONFIG = CORE_CONFIG.replace(
    'profiles = ["core"]',
    'profiles = ["core", "roadmap-issues"]',
)


class RoadmapIssuesProfileTests(unittest.TestCase):
    def _repo(self, temp: str, config_text: str = CORE_CONFIG) -> tuple[Path, Path]:
        root = Path(temp)
        config = root / ".agentic-repo.toml"
        config.write_text(config_text, encoding="utf-8")
        (root / "ROADMAP.md").write_text(
            "# Roadmap\n\n"
            "## T1 — First\n\n"
            "- **Status:** Open\n"
            "- **Priority:** High\n"
            "- **Depends on:** none\n\n"
            "## T2 — Second\n\n"
            "- **Status:** Open\n"
            "- **Priority:** High\n"
            "- **Depends on:** T1\n",
            encoding="utf-8",
        )
        return root, config

    def test_profile_is_discoverable_and_opt_in(self) -> None:
        self.assertIn("roadmap-issues", available_profiles())

        with tempfile.TemporaryDirectory() as temp:
            root, config = self._repo(temp, ISSUES_CONFIG)
            bootstrap(root, config)
            agents = (root / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("<!-- agentic-roadmap-issue:v1 -->", agents)
            self.assertIn("Roadmap item: <ID>", agents)
            self.assertIn("Canonical source:", agents)
            self.assertIn("Source revision:", agents)
            self.assertIn("Scheduler state:", agents)
            self.assertIn("Blocked by:", agents)
            self.assertIn("Unblocks:", agents)
            self.assertTrue(check(root, config).ok)

        with tempfile.TemporaryDirectory() as temp:
            root, config = self._repo(temp, CORE_CONFIG)
            bootstrap(root, config)
            agents = (root / "AGENTS.md").read_text(encoding="utf-8")
            self.assertNotIn("agentic-roadmap-issue:v1", agents)
            self.assertTrue(check(root, config).ok)

    def test_profile_preserves_roadmap_authority_and_revalidation(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root, config = self._repo(temp, ISSUES_CONFIG)
            bootstrap(root, config)
            agents = (root / "AGENTS.md").read_text(encoding="utf-8")
            playbook = (root / "docs/agent-playbook.md").read_text(encoding="utf-8")
            pr_template = (root / ".github/pull_request_template.md").read_text(encoding="utf-8")

            self.assertIn("derived scheduling view, never a competing source of truth", agents)
            self.assertIn("the roadmap wins", agents)
            self.assertIn("re-read the current canonical roadmap item", agents)
            self.assertIn("Never mark a dependent `READY` merely because one predecessor completed", playbook)
            self.assertIn("Projection reconciliation must be idempotent", playbook)
            self.assertIn("one or more GitHub Issue updates did not", playbook)
            self.assertIn("do not use automatic Issue closure for partial progress", pr_template)

    def test_upgrade_enables_profile_without_new_managed_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root, config = self._repo(temp, CORE_CONFIG)
            bootstrap(root, config)
            config.write_text(ISSUES_CONFIG, encoding="utf-8")

            changed = set(upgrade(root, config))

            self.assertEqual(
                {
                    "AGENTS.md",
                    "docs/agent-playbook.md",
                    ".github/pull_request_template.md",
                    ".agentic-repo.lock.json",
                },
                changed,
            )
            self.assertTrue(check(root, config).ok)


if __name__ == "__main__":
    unittest.main()
