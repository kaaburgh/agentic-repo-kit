from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from agentic_repo_kit.distribution import distribution_identity
from scripts.build_pyz import build_pyz


ROOT = Path(__file__).resolve().parents[1]
CONFIG = '''\
kit_version = 1
profiles = ["core"]

[project]
name = "Executable fixture"
kind = "test"
roadmap = "ROADMAP.md"
'''


class ExecutableDistributionTests(unittest.TestCase):
    def test_zipapp_build_is_reproducible_and_matches_committed_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            first = Path(temp) / "first.pyz"
            second = Path(temp) / "second.pyz"
            first_digest = build_pyz(ROOT, first)
            second_digest = build_pyz(ROOT, second)

            self.assertEqual(first.read_bytes(), second.read_bytes())
            self.assertEqual(first_digest, second_digest)
            self.assertEqual(first_digest, distribution_identity()["sha256"])

    def test_zipapp_bootstrap_writes_its_own_distribution_identity(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_root = Path(temp)
            artifact = temp_root / "agentic-repo-kit.pyz"
            digest = build_pyz(ROOT, artifact)
            repo = temp_root / "repo"
            repo.mkdir()
            (repo / ".agentic-repo.toml").write_text(CONFIG, encoding="utf-8")
            (repo / "ROADMAP.md").write_text("# Roadmap\n", encoding="utf-8")

            bootstrap = subprocess.run(
                [sys.executable, str(artifact), "bootstrap", str(repo)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, bootstrap.returncode, bootstrap.stderr)
            lock = json.loads((repo / ".agentic-repo.lock.json").read_text(encoding="utf-8"))
            self.assertEqual(2, lock["format"])
            self.assertEqual(digest, lock["distribution"]["sha256"])
            self.assertEqual("agentic-repo-kit-0.1.8.pyz", lock["distribution"]["artifact"])

            check = subprocess.run(
                [sys.executable, str(artifact), "check", str(repo)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, check.returncode, check.stderr)
            self.assertIn("consistent", check.stdout)

    def test_distribution_metadata_is_not_embedded_in_zipapp(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            artifact = Path(temp) / "agentic-repo-kit.pyz"
            build_pyz(ROOT, artifact)
            import zipfile

            with zipfile.ZipFile(artifact) as zf:
                self.assertNotIn("agentic_repo_kit/distribution.json", zf.namelist())


if __name__ == "__main__":
    unittest.main()
