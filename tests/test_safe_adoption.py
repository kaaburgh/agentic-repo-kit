from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from agentic_repo_kit import adoption
from agentic_repo_kit.adoption import apply_adoption, build_adoption_plan
from agentic_repo_kit.errors import AgenticRepoError
from agentic_repo_kit.operations import bootstrap, check, upgrade
from agentic_repo_kit.render import GENERATED_MARKER


CORE_CONFIG = '''\
kit_version = 1
profiles = ["core"]

[project]
name = "Mature fixture"
kind = "test / existing hand-written contract"
roadmap = "ROADMAP.md"
'''

ASCENDANCY_CONFIG = '''\
kit_version = 1
profiles = [
  "core",
  "reverse-engineering",
  "blind-research",
  "proprietary-target",
  "native-binary-patching",
]

[project]
name = "Ascendancy-shaped fixture"
kind = "closed-source game mod / native binary patching"
roadmap = "ROADMAP.md"

[workflow]
cloud_first = true

[local]
policy_files = ["blind-research.local.md"]
'''


class SafeAdoptionTests(unittest.TestCase):
    def make_repo(self, config: str = CORE_CONFIG) -> tuple[tempfile.TemporaryDirectory, Path]:
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        (root / ".agentic-repo.toml").write_text(config, encoding="utf-8")
        (root / "ROADMAP.md").write_text("# Roadmap\n", encoding="utf-8")
        return temp, root

    def snapshot_files(self, root: Path) -> dict[str, bytes]:
        return {
            str(path.relative_to(root)): path.read_bytes()
            for path in root.rglob("*")
            if path.is_file()
        }

    def test_plan_is_non_destructive_and_exposes_unmanaged_replacements(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        (root / "AGENTS.md").write_text("# Legacy agents\n\nLegacy-only rule.\n", encoding="utf-8")
        pr = root / ".github/pull_request_template.md"
        pr.parent.mkdir(parents=True)
        pr.write_text("# Legacy PR template\n", encoding="utf-8")
        before = self.snapshot_files(root)

        plan = build_adoption_plan(root, root / ".agentic-repo.toml")

        self.assertEqual(before, self.snapshot_files(root))
        self.assertFalse((root / ".agentic-repo.lock.json").exists())
        self.assertRegex(plan.plan_id, r"^[0-9a-f]{64}$")
        by_path = {item.path: item for item in plan.files}
        self.assertEqual("replace_unmanaged", by_path["AGENTS.md"].action)
        self.assertEqual("replace_unmanaged", by_path[".github/pull_request_template.md"].action)
        self.assertIn("Legacy-only rule.", by_path["AGENTS.md"].diff or "")
        self.assertTrue(any("Review every replace_unmanaged diff" in item for item in plan.operator_decisions))

    def test_stale_or_malformed_plan_token_fails_without_transfer(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        agents = root / "AGENTS.md"
        agents.write_text("# Legacy agents\n", encoding="utf-8")
        plan = build_adoption_plan(root, root / ".agentic-repo.toml")

        with self.assertRaisesRegex(AgenticRepoError, "64-hex-character"):
            apply_adoption(root, root / ".agentic-repo.toml", "z" * 64)

        agents.write_text("# Legacy agents\n\nChanged after review.\n", encoding="utf-8")
        with self.assertRaisesRegex(AgenticRepoError, "adoption plan changed"):
            apply_adoption(root, root / ".agentic-repo.toml", plan.plan_id)

        self.assertEqual("# Legacy agents\n\nChanged after review.\n", agents.read_text(encoding="utf-8"))
        self.assertFalse((root / ".agentic-repo.lock.json").exists())

    def test_local_fragment_survives_transfer_and_normal_upgrade_owns_outputs(self) -> None:
        config = CORE_CONFIG + '\n[local]\npolicy_files = ["docs/agent-policy.local.md"]\n'
        temp, root = self.make_repo(config)
        self.addCleanup(temp.cleanup)
        agents = root / "AGENTS.md"
        agents.write_text("# Hand-written agents\n\nProject-only behavior.\n", encoding="utf-8")
        local = root / "docs/agent-policy.local.md"
        local.parent.mkdir(parents=True)
        local_text = "## Project-only behavior\n\nPreserve this through managed generation.\n"
        local.write_text(local_text, encoding="utf-8")

        plan = build_adoption_plan(root, root / ".agentic-repo.toml")
        changed = apply_adoption(root, root / ".agentic-repo.toml", plan.plan_id)

        self.assertIn("AGENTS.md", changed)
        self.assertIn(".agentic-repo.lock.json", changed)
        generated_agents = agents.read_text(encoding="utf-8")
        self.assertIn(GENERATED_MARKER, generated_agents)
        self.assertIn("Preserve this through managed generation.", generated_agents)
        self.assertEqual(local_text, local.read_text(encoding="utf-8"))
        self.assertTrue(check(root, root / ".agentic-repo.toml").ok)
        self.assertEqual([], upgrade(root, root / ".agentic-repo.toml"))

    def test_existing_managed_lock_routes_to_upgrade(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        bootstrap(root, root / ".agentic-repo.toml")

        with self.assertRaisesRegex(AgenticRepoError, "use upgrade instead"):
            build_adoption_plan(root, root / ".agentic-repo.toml")

    def test_local_input_cannot_overlap_managed_output(self) -> None:
        config = CORE_CONFIG + '\n[local]\npolicy_files = ["AGENTS.md"]\n'
        temp, root = self.make_repo(config)
        self.addCleanup(temp.cleanup)
        (root / "AGENTS.md").write_text("# Legacy agents\n", encoding="utf-8")

        with self.assertRaisesRegex(AgenticRepoError, "overlaps a generated managed output"):
            build_adoption_plan(root, root / ".agentic-repo.toml")

    def test_apply_rolls_back_all_files_and_never_leaves_lock_on_write_failure(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        (root / "AGENTS.md").write_text("# Legacy agents\n", encoding="utf-8")
        before = self.snapshot_files(root)
        plan = build_adoption_plan(root, root / ".agentic-repo.toml")
        original_replace = adoption._atomic_replace_text
        writes = 0

        def fail_second_write(path: Path, content: str) -> None:
            nonlocal writes
            writes += 1
            if writes == 2:
                raise OSError("synthetic adoption write failure")
            original_replace(path, content)

        with patch("agentic_repo_kit.adoption._atomic_replace_text", side_effect=fail_second_write):
            with self.assertRaisesRegex(AgenticRepoError, "was rolled back"):
                apply_adoption(root, root / ".agentic-repo.toml", plan.plan_id)

        self.assertEqual(before, self.snapshot_files(root))
        self.assertFalse((root / ".agentic-repo.lock.json").exists())

    def test_ascendancy_shaped_fixture_preserves_blind_gate_as_local_policy(self) -> None:
        temp, root = self.make_repo(ASCENDANCY_CONFIG)
        self.addCleanup(temp.cleanup)
        (root / "AGENTS.md").write_text(
            "# Existing Ascendancy contract\n\nLegacy generic RE rules plus project gate.\n",
            encoding="utf-8",
        )
        pr = root / ".github/pull_request_template.md"
        pr.parent.mkdir(parents=True)
        pr.write_text("# Existing Ascendancy PR template\n", encoding="utf-8")
        gate = root / "blind-research.local.md"
        gate_text = (
            "## Project blind-research gate\n\n"
            "The blind-research gate remains active until M1 is Completed and verified.\n"
        )
        gate.write_text(gate_text, encoding="utf-8")

        plan = build_adoption_plan(root, root / ".agentic-repo.toml")
        by_path = {item.path: item for item in plan.files}
        self.assertEqual("replace_unmanaged", by_path["AGENTS.md"].action)
        self.assertEqual("replace_unmanaged", by_path[".github/pull_request_template.md"].action)

        apply_adoption(root, root / ".agentic-repo.toml", plan.plan_id)

        agents = (root / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("Blind research provenance", agents)
        self.assertIn("The blind-research gate remains active until M1", agents)
        self.assertEqual(gate_text, gate.read_text(encoding="utf-8"))
        self.assertTrue(check(root, root / ".agentic-repo.toml").ok)


if __name__ == "__main__":
    unittest.main()
