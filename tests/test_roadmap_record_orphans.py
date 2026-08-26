from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from agentic_repo_kit.errors import AgenticRepoError
from agentic_repo_kit.operations import bootstrap, check


BASE_CONFIG = '''\
kit_version = 1
profiles = ["core"]

[project]
name = "Record coverage fixture"
kind = "test"
roadmap = "ROADMAP.md"
'''

ROADMAP = '''\
# Roadmap

### R1 — Current investigation
- **Status:** Open
- **Depends on:** none
- **Known evidence:** [linked record](docs/experiments/linked.md)

The item section can also carry [a prose record](docs/experiments/prose.md#result).

### R2 — Other work
- **Status:** Open
- **Depends on:** none
'''


class RecordOrphanTests(unittest.TestCase):
    def make_repo(self, *, configured: bool) -> Path:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        config = BASE_CONFIG
        if configured:
            config += '\n[roadmap]\nrecord_directories = ["docs/experiments"]\n'
        (root / ".agentic-repo.toml").write_text(config, encoding="utf-8")
        (root / "ROADMAP.md").write_text(ROADMAP, encoding="utf-8")
        bootstrap(root, root / ".agentic-repo.toml")
        records = root / "docs/experiments"
        records.mkdir(parents=True, exist_ok=True)
        for name in ("linked.md", "prose.md", "orphan-a.md", "orphan-b.json"):
            (records / name).write_text(name, encoding="utf-8")
        return root

    def test_configured_directory_reports_count_and_list(self) -> None:
        root = self.make_repo(configured=True)
        result = check(root, root / ".agentic-repo.toml")

        self.assertTrue(result.ok, result.problems)
        record_warnings = [warning for warning in result.warnings if "configured durable record" in warning]
        self.assertEqual(1, len(record_warnings))
        self.assertIn("2 configured durable record(s)", record_warnings[0])
        self.assertIn("docs/experiments/orphan-a.md", record_warnings[0])
        self.assertIn("docs/experiments/orphan-b.json", record_warnings[0])
        self.assertNotIn("docs/experiments/linked.md", record_warnings[0])
        self.assertNotIn("docs/experiments/prose.md", record_warnings[0])

    def test_no_configuration_is_inert(self) -> None:
        root = self.make_repo(configured=False)
        result = check(root, root / ".agentic-repo.toml")
        self.assertTrue(result.ok, result.problems)
        self.assertFalse(any("configured durable record" in warning for warning in result.warnings))

    def test_links_outside_item_sections_do_not_count(self) -> None:
        root = self.make_repo(configured=True)
        roadmap = (root / "ROADMAP.md").read_text(encoding="utf-8")
        roadmap += "\n## Notes\n\n[orphan](docs/experiments/orphan-a.md)\n"
        (root / "ROADMAP.md").write_text(roadmap, encoding="utf-8")

        result = check(root, root / ".agentic-repo.toml")
        warning = next(w for w in result.warnings if "configured durable record" in w)
        self.assertIn("docs/experiments/orphan-a.md", warning)

    def test_missing_configured_directory_is_warning_only(self) -> None:
        root = self.make_repo(configured=True)
        for path in (root / "docs/experiments").iterdir():
            path.unlink()
        (root / "docs/experiments").rmdir()

        result = check(root, root / ".agentic-repo.toml")
        self.assertTrue(result.ok, result.problems)
        self.assertIn(
            "configured roadmap record directory does not exist: docs/experiments",
            result.warnings,
        )

    def test_record_directory_must_be_repository_relative(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / ".agentic-repo.toml").write_text(
                BASE_CONFIG + '\n[roadmap]\nrecord_directories = ["../records"]\n',
                encoding="utf-8",
            )
            (root / "ROADMAP.md").write_text("# Roadmap\n", encoding="utf-8")
            with self.assertRaisesRegex(AgenticRepoError, "repository-relative and confined"):
                bootstrap(root, root / ".agentic-repo.toml")


if __name__ == "__main__":
    unittest.main()
