from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from agentic_repo_kit.config import load_config
from agentic_repo_kit.errors import AgenticRepoError
from agentic_repo_kit.operations import bootstrap, check, upgrade


CONFIG = '''\
kit_version = 1
profiles = ["core"]

[project]
name = "Workflow fixture"
kind = "test"
roadmap = "ROADMAP.md"
'''
WORKFLOW = ".github/workflows/agentic-repo-check.yml"


class ManagedCheckWorkflowTests(unittest.TestCase):
    def _repo(self, temp: str) -> tuple[Path, Path]:
        root = Path(temp)
        config = root / ".agentic-repo.toml"
        config.write_text(CONFIG, encoding="utf-8")
        (root / "ROADMAP.md").write_text("# Roadmap\n", encoding="utf-8")
        return root, config

    def test_bootstrap_generates_lock_driven_public_check_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root, config = self._repo(temp)
            changed = bootstrap(root, config)
            self.assertIn(WORKFLOW, changed)

            workflow = (root / WORKFLOW).read_text(encoding="utf-8")
            self.assertIn(".agentic-repo.lock.json", workflow)
            self.assertIn('lock.get("format") != 2', workflow)
            self.assertIn('distribution.get("sha256")', workflow)
            self.assertIn("releases/download", workflow)
            self.assertIn("curl --fail --location --proto '=https'", workflow)
            self.assertIn("artifact digest mismatch", workflow)
            self.assertIn('python "$KIT_PATH" check .', workflow)
            self.assertIn("contents: read", workflow)
            self.assertIn("pull_request:", workflow)
            self.assertIn("push:", workflow)
            self.assertNotIn("latest", workflow.lower())
            self.assertNotIn("secrets.", workflow)
            self.assertNotIn("paths:", workflow)

            lock = json.loads((root / ".agentic-repo.lock.json").read_text(encoding="utf-8"))
            self.assertIn(WORKFLOW, lock["generated"])
            self.assertTrue(check(root, config).ok)

    def test_check_detects_managed_workflow_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root, config = self._repo(temp)
            bootstrap(root, config)
            path = root / WORKFLOW
            path.write_text(path.read_text(encoding="utf-8") + "# drift\n", encoding="utf-8")

            result = check(root, config)
            self.assertFalse(result.ok)
            self.assertIn(f"generated file drift: {WORKFLOW}", result.problems)

    def test_upgrade_adds_workflow_to_pre_ark13_managed_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root, config = self._repo(temp)
            bootstrap(root, config)
            workflow = root / WORKFLOW
            workflow.unlink()
            lock_path = root / ".agentic-repo.lock.json"
            lock = json.loads(lock_path.read_text(encoding="utf-8"))
            del lock["generated"][WORKFLOW]
            lock_path.write_text(json.dumps(lock, indent=2, sort_keys=True) + "\n", encoding="utf-8")

            changed = upgrade(root, config)
            self.assertIn(WORKFLOW, changed)
            self.assertTrue(workflow.is_file())
            self.assertTrue(check(root, config).ok)

    def test_upgrade_refuses_unmanaged_same_name_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root, config = self._repo(temp)
            bootstrap(root, config)
            workflow = root / WORKFLOW
            lock_path = root / ".agentic-repo.lock.json"
            lock = json.loads(lock_path.read_text(encoding="utf-8"))
            del lock["generated"][WORKFLOW]
            lock_path.write_text(json.dumps(lock, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            workflow.write_text("name: project-owned workflow\n", encoding="utf-8")

            with self.assertRaisesRegex(AgenticRepoError, "refusing to overwrite unmanaged or drifted file"):
                upgrade(root, config)


if __name__ == "__main__":
    unittest.main()
