from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from agentic_repo_kit.operations import bootstrap, check, upgrade


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

        self.assertIn("single source of truth for planning state", agents)
        self.assertIn("derived projection, never as a second source of truth", agents)
        self.assertIn("changes current operator actions or instructions", agents)
        self.assertIn("referenced commands, flags, preflight steps, scripts", agents)
        self.assertIn("ready/current `LOCAL ONLY` work", agents)
        self.assertIn("Completed items, blocked downstream items, and purely cloud-executable items", agents)
        self.assertIn("Do not assume a file is named `NEXT-STEPS.md`", agents)
        self.assertIn("procedural docs/scripts/tooling", playbook)
        self.assertIn("sources supply procedure rather than competing readiness or sequencing state", roadmap_authoring)
        self.assertIn("Use the roadmap to decide what is current, ready, blocked, or sequenced", roadmap_authoring)
        self.assertIn("cannot be assumed to semantically derive or prove the correctness", roadmap_authoring)
        self.assertTrue(check(root, root / ".agentic-repo.toml").ok)

    def test_upgrade_propagates_policy_without_owning_local_projection(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        local_policy = root / "operator-local.md"
        local_policy_text = (
            "## Project operator projection\n\n"
            "`ROADMAP.md` is authoritative; `NEXT-STEPS.md` is the operator-facing projection.\n"
        )
        local_policy.write_text(local_policy_text, encoding="utf-8")
        projection = root / "NEXT-STEPS.md"
        projection_text = "# Operator checklist\n\n- [ ] Preserve this project-owned checklist.\n"
        projection.write_text(projection_text, encoding="utf-8")
        (root / ".agentic-repo.toml").write_text(
            CONFIG + '\n[local]\npolicy_files = ["operator-local.md"]\n',
            encoding="utf-8",
        )
        bootstrap(root, root / ".agentic-repo.toml")

        agents_path = root / "AGENTS.md"
        agents = agents_path.read_text(encoding="utf-8")
        start = agents.index("## Operator-facing derived projections")
        end = agents.index("## Validation and claims", start)
        agents_path.write_text(agents[:start] + agents[end:], encoding="utf-8")

        changed = upgrade(root, root / ".agentic-repo.toml")
        self.assertIn("AGENTS.md", changed)
        restored = agents_path.read_text(encoding="utf-8")
        self.assertIn("derived projection, never as a second source of truth", restored)
        self.assertIn("Project operator projection", restored)
        self.assertEqual(local_policy_text, local_policy.read_text(encoding="utf-8"))
        self.assertEqual(projection_text, projection.read_text(encoding="utf-8"))
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
