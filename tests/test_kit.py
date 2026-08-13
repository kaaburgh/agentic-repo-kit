from __future__ import annotations

import contextlib
import io
from pathlib import Path
import tempfile
import unittest

from agentic_repo_kit.cli import main
from agentic_repo_kit.config import load_config
from agentic_repo_kit.errors import AgenticRepoError
from agentic_repo_kit.operations import bootstrap, check, roadmap_normalization_packet, upgrade
from agentic_repo_kit.profiles import available_profiles


CONFIG = '''\
kit_version = 1
profiles = ["core", "reverse-engineering"]

[project]
name = "Fixture"
kind = "test"
roadmap = "ROADMAP.md"
'''


class KitTests(unittest.TestCase):
    def make_repo(self) -> tuple[tempfile.TemporaryDirectory, Path]:
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        (root / ".agentic-repo.toml").write_text(CONFIG, encoding="utf-8")
        (root / "ROADMAP.md").write_text("# Roadmap\n", encoding="utf-8")
        return temp, root

    def test_profiles_cover_initial_domains(self) -> None:
        profiles = set(available_profiles())
        self.assertTrue({"core", "reverse-engineering", "native-binary-patching", "emulator", "graphics", "upstream-first"} <= profiles)

    def test_bootstrap_and_check(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        changed = bootstrap(root, root / ".agentic-repo.toml")
        self.assertIn("AGENTS.md", changed)
        self.assertTrue((root / "docs/re/README.md").exists())
        self.assertTrue(check(root, root / ".agentic-repo.toml").ok)

    def test_check_detects_generated_drift(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        bootstrap(root, root / ".agentic-repo.toml")
        (root / "AGENTS.md").write_text("drift\n", encoding="utf-8")
        result = check(root, root / ".agentic-repo.toml")
        self.assertFalse(result.ok)
        self.assertIn("generated file drift: AGENTS.md", result.problems)

    def test_bootstrap_refuses_unmanaged_overwrite(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        (root / "AGENTS.md").write_text("hand-written\n", encoding="utf-8")
        with self.assertRaises(AgenticRepoError):
            bootstrap(root, root / ".agentic-repo.toml")

    def test_upgrade_repairs_managed_drift(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        bootstrap(root, root / ".agentic-repo.toml")
        path = root / "AGENTS.md"
        original = path.read_text(encoding="utf-8")
        path.write_text(original + "\nlocal accidental edit\n", encoding="utf-8")
        changed = upgrade(root, root / ".agentic-repo.toml")
        self.assertIn("AGENTS.md", changed)
        self.assertEqual(original, path.read_text(encoding="utf-8"))

    def test_unknown_profile_fails_closed(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        (root / ".agentic-repo.toml").write_text(CONFIG.replace("reverse-engineering", "missing-profile"), encoding="utf-8")
        with self.assertRaises(AgenticRepoError):
            bootstrap(root, root / ".agentic-repo.toml")

    def test_local_policy_fragment_is_composed(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        (root / "local.md").write_text("## Fixture-specific rule\n\nKeep the fixture tiny.\n", encoding="utf-8")
        config = CONFIG + '\n[local]\npolicy_files = ["local.md"]\n'
        (root / ".agentic-repo.toml").write_text(config, encoding="utf-8")
        bootstrap(root, root / ".agentic-repo.toml")
        self.assertIn("Fixture-specific rule", (root / "AGENTS.md").read_text(encoding="utf-8"))

    def test_normalization_packet_contains_inspection_and_skill(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        config = load_config(root / ".agentic-repo.toml")
        packet = roadmap_normalization_packet(root, config)
        self.assertIn("Roadmap normalization packet for Fixture", packet)
        self.assertIn("Expected information gain", packet.replace("expected information gain", "Expected information gain"))
        self.assertIn("Repository inspection", packet)

    def test_cli_check_exit_code(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        bootstrap(root, root / ".agentic-repo.toml")
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = main(["check", str(root)])
        self.assertEqual(0, code)
        self.assertIn("consistent", stdout.getvalue())

    def test_unsupported_kit_version_fails_closed(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        (root / ".agentic-repo.toml").write_text(CONFIG.replace("kit_version = 1", "kit_version = 2"), encoding="utf-8")
        with self.assertRaises(AgenticRepoError):
            load_config(root / ".agentic-repo.toml")

    def test_workflow_boolean_type_is_validated(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        bad = CONFIG + '\n[workflow]\ncloud_first = "yes"\n'
        (root / ".agentic-repo.toml").write_text(bad, encoding="utf-8")
        with self.assertRaises(AgenticRepoError):
            load_config(root / ".agentic-repo.toml")


if __name__ == "__main__":
    unittest.main()
