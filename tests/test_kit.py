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

    def test_bootstrap_preflights_all_outputs_before_writing(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        pr_template = root / ".github/pull_request_template.md"
        pr_template.parent.mkdir(parents=True)
        pr_template.write_text("hand-written\n", encoding="utf-8")

        with self.assertRaises(AgenticRepoError):
            bootstrap(root, root / ".agentic-repo.toml")

        self.assertFalse((root / "AGENTS.md").exists())
        self.assertFalse((root / "docs/agent-playbook.md").exists())
        self.assertEqual("hand-written\n", pr_template.read_text(encoding="utf-8"))

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

    def test_upgrade_removes_obsolete_managed_outputs(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        bootstrap(root, root / ".agentic-repo.toml")
        self.assertTrue((root / "docs/re/README.md").exists())
        self.assertTrue((root / "docs/experiments/README.md").exists())

        (root / ".agentic-repo.toml").write_text(
            CONFIG.replace('["core", "reverse-engineering"]', '["core"]'),
            encoding="utf-8",
        )
        changed = upgrade(root, root / ".agentic-repo.toml")

        self.assertIn("docs/re/README.md", changed)
        self.assertIn("docs/experiments/README.md", changed)
        self.assertFalse((root / "docs/re/README.md").exists())
        self.assertFalse((root / "docs/experiments/README.md").exists())
        self.assertTrue(check(root, root / ".agentic-repo.toml").ok)

    def test_upgrade_refuses_to_remove_unmanaged_obsolete_output(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        bootstrap(root, root / ".agentic-repo.toml")
        stale = root / "docs/re/README.md"
        stale.write_text("hand-written replacement\n", encoding="utf-8")
        (root / ".agentic-repo.toml").write_text(
            CONFIG.replace('["core", "reverse-engineering"]', '["core"]'),
            encoding="utf-8",
        )

        with self.assertRaises(AgenticRepoError):
            upgrade(root, root / ".agentic-repo.toml")

        self.assertEqual("hand-written replacement\n", stale.read_text(encoding="utf-8"))

    def test_generated_output_rejects_symlinked_parent(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        victim_temp = tempfile.TemporaryDirectory()
        self.addCleanup(victim_temp.cleanup)
        victim = Path(victim_temp.name)
        (root / "docs").symlink_to(victim, target_is_directory=True)

        with self.assertRaises(AgenticRepoError):
            bootstrap(root, root / ".agentic-repo.toml")

        self.assertFalse((victim / "agent-playbook.md").exists())
        self.assertFalse((root / "AGENTS.md").exists())

    def test_upgrade_rejects_symlinked_lock_file(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        victim = root / "victim.txt"
        victim.write_text("do not overwrite\n", encoding="utf-8")
        (root / ".agentic-repo.lock.json").symlink_to(victim)

        with self.assertRaises(AgenticRepoError):
            upgrade(root, root / ".agentic-repo.toml")

        self.assertEqual("do not overwrite\n", victim.read_text(encoding="utf-8"))

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

    def test_local_fragment_rejects_path_traversal(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        secret = root.parent / "agentic-repo-kit-secret.md"
        secret.write_text("secret\n", encoding="utf-8")
        self.addCleanup(lambda: secret.unlink(missing_ok=True))
        config = CONFIG + '\n[local]\npolicy_files = ["../agentic-repo-kit-secret.md"]\n'
        (root / ".agentic-repo.toml").write_text(config, encoding="utf-8")

        with self.assertRaises(AgenticRepoError):
            bootstrap(root, root / ".agentic-repo.toml")

    def test_local_fragment_rejects_absolute_path(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        config = CONFIG + '\n[local]\npolicy_files = ["/etc/passwd"]\n'
        (root / ".agentic-repo.toml").write_text(config, encoding="utf-8")
        with self.assertRaises(AgenticRepoError):
            bootstrap(root, root / ".agentic-repo.toml")

    def test_local_fragment_rejects_symlink(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        outside_temp = tempfile.TemporaryDirectory()
        self.addCleanup(outside_temp.cleanup)
        outside = Path(outside_temp.name) / "policy.md"
        outside.write_text("private\n", encoding="utf-8")
        (root / "local.md").symlink_to(outside)
        config = CONFIG + '\n[local]\npolicy_files = ["local.md"]\n'
        (root / ".agentic-repo.toml").write_text(config, encoding="utf-8")

        with self.assertRaises(AgenticRepoError):
            bootstrap(root, root / ".agentic-repo.toml")

    def test_unknown_configuration_keys_fail_closed(self) -> None:
        cases = {
            "top-level": CONFIG.replace("\n[project]", "\nunknown = true\n\n[project]"),
            "project": CONFIG.replace('roadmap = "ROADMAP.md"', 'roadmap = "ROADMAP.md"\nunknown = true'),
            "workflow": CONFIG + '\n[workflow]\nunknown = true\n',
            "local": CONFIG + '\n[local]\npolicy_file = ["local.md"]\n',
        }
        for name, config in cases.items():
            with self.subTest(name=name):
                temp, root = self.make_repo()
                self.addCleanup(temp.cleanup)
                (root / ".agentic-repo.toml").write_text(config, encoding="utf-8")
                with self.assertRaises(AgenticRepoError):
                    load_config(root / ".agentic-repo.toml")

    def test_unsupported_workflow_toggles_fail_closed(self) -> None:
        for key in ("roadmap_driven", "one_roadmap_item_per_pr"):
            with self.subTest(key=key):
                temp, root = self.make_repo()
                self.addCleanup(temp.cleanup)
                bad = CONFIG + f'\n[workflow]\n{key} = false\n'
                (root / ".agentic-repo.toml").write_text(bad, encoding="utf-8")
                with self.assertRaises(AgenticRepoError):
                    load_config(root / ".agentic-repo.toml")

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
