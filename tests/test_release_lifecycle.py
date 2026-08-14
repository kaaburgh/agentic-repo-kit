from __future__ import annotations

import json
from pathlib import Path
import tomllib
import unittest

from agentic_repo_kit import __version__
from agentic_repo_kit.distribution import artifact_name, distribution_identity, release_tag


ROOT = Path(__file__).resolve().parents[1]


class ReleaseLifecycleTests(unittest.TestCase):
    def test_version_identity_is_consistent(self) -> None:
        pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        lock = json.loads((ROOT / ".agentic-repo.lock.json").read_text(encoding="utf-8"))

        self.assertEqual(__version__, pyproject["project"]["version"])
        self.assertEqual(__version__, lock["tool_version"])
        self.assertEqual(2, lock["format"])
        self.assertEqual(distribution_identity(), lock["distribution"])
        self.assertEqual(artifact_name(), lock["distribution"]["artifact"])
        self.assertEqual(release_tag(), lock["distribution"]["release"])

    def test_release_workflow_preserves_exact_version_target_and_supports_explicit_recovery(self) -> None:
        workflow = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")

        self.assertIn("branches: [main]", workflow)
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("target_sha:", workflow)
        self.assertIn("contents: write", workflow)
        self.assertIn("cancel-in-progress: false", workflow)
        self.assertIn("agentic_repo_kit/__init__.py", workflow)
        self.assertIn("pyproject.toml", workflow)
        self.assertIn('target_sha="$CURRENT_SHA"', workflow)
        self.assertIn("workflow_dispatch target_sha must be an exact 40-character lowercase commit SHA", workflow)
        self.assertIn("git merge-base --is-ancestor", workflow)
        self.assertIn('git checkout --detach "$TARGET_SHA"', workflow)
        self.assertIn("existing tag $TAG points to", workflow)
        self.assertIn("assets_complete", workflow)
        self.assertIn("gh release download", workflow)
        self.assertIn("existing executable asset digest mismatch", workflow)
        self.assertIn("distribution\"][\"sha256", workflow)
        self.assertIn("scripts/build_pyz.py", workflow)
        self.assertIn("executable artifact digest mismatch", workflow)
        self.assertIn('agentic-repo-kit-$VERSION.pyz', workflow)
        self.assertIn("git archive --format=tar", workflow)
        self.assertIn("git archive --format=zip", workflow)
        self.assertIn("gzip -n", workflow)
        self.assertIn("SHA256SUMS", workflow)
        self.assertIn("gh release create", workflow)
        self.assertIn("gh release upload", workflow)
        self.assertIn("--clobber", workflow)
        self.assertIn('--target "$RELEASE_SHA"', workflow)

    def test_ark12_one_time_recovery_target_is_explicit_until_release_exists(self) -> None:
        workflow = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
        self.assertIn('version" == "0.1.8', workflow)
        self.assertIn("f95068f36c839cc2df21cea3067674b3f7679c9a", workflow)
        self.assertIn("Remove this fallback after v0.1.8 is verified", workflow)


if __name__ == "__main__":
    unittest.main()
