from __future__ import annotations

import os
from pathlib import Path
import stat
import tempfile
import unittest

from agentic_repo_kit.adoption import adoption_report, apply_adoption, build_adoption_plan
from agentic_repo_kit.cli import _write_adoption_report
from agentic_repo_kit.errors import AgenticRepoError


CORE = '''\
kit_version = 1
profiles = ["core"]

[project]
name = "Review fixture"
kind = "test"
roadmap = "ROADMAP.md"
'''


class SafeAdoptionReviewRegressionTests(unittest.TestCase):
    def make_repo(self, config: str = CORE) -> tuple[tempfile.TemporaryDirectory, Path]:
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        (root / ".agentic-repo.toml").write_text(config, encoding="utf-8")
        (root / "ROADMAP.md").write_text("# Roadmap\n", encoding="utf-8")
        return temp, root

    def test_canonical_alias_of_managed_output_is_rejected_as_local_input(self) -> None:
        config = CORE + '\n[local]\npolicy_files = ["./AGENTS.md"]\n'
        temp, root = self.make_repo(config)
        self.addCleanup(temp.cleanup)
        (root / "AGENTS.md").write_text("# Legacy\n", encoding="utf-8")

        with self.assertRaisesRegex(AgenticRepoError, "aliases generated output 'AGENTS.md'"):
            build_adoption_plan(root, root / ".agentic-repo.toml")

    def test_plan_output_refuses_managed_input_and_existing_paths(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        (root / "AGENTS.md").write_text("# Legacy\n", encoding="utf-8")
        plan = build_adoption_plan(root, root / ".agentic-repo.toml")
        report = adoption_report(plan)

        with self.assertRaisesRegex(AgenticRepoError, "collides with an adoption input/managed path"):
            _write_adoption_report(
                str(root / ".agentic-repo.lock.json"),
                root=root,
                config_path=root / ".agentic-repo.toml",
                plan=plan,
                report=report,
            )

        existing = root / "reviewed-plan.json"
        existing.write_text("keep me\n", encoding="utf-8")
        with self.assertRaisesRegex(AgenticRepoError, "refusing to overwrite"):
            _write_adoption_report(
                str(existing),
                root=root,
                config_path=root / ".agentic-repo.toml",
                plan=plan,
                report=report,
            )
        self.assertEqual("keep me\n", existing.read_text(encoding="utf-8"))

    @unittest.skipUnless(os.name == "posix", "POSIX mode semantics")
    def test_apply_preserves_existing_mode_and_creates_readable_managed_files(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        agents = root / "AGENTS.md"
        agents.write_text("# Legacy\n", encoding="utf-8")
        os.chmod(agents, 0o640)
        plan = build_adoption_plan(root, root / ".agentic-repo.toml")

        apply_adoption(root, root / ".agentic-repo.toml", plan.plan_id)

        self.assertEqual(0o640, stat.S_IMODE(agents.stat().st_mode))
        self.assertEqual(0o644, stat.S_IMODE((root / ".agentic-repo.lock.json").stat().st_mode))


if __name__ == "__main__":
    unittest.main()
