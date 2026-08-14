from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import unittest

from scripts.resolve_release_target import resolve_release_target


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()


def _write_version(root: Path, version: str) -> None:
    package = root / "agentic_repo_kit"
    package.mkdir(exist_ok=True)
    (package / "__init__.py").write_text(
        f'__version__ = "{version}"\n',
        encoding="utf-8",
    )
    (root / "pyproject.toml").write_text(
        "[project]\n"
        'name = "fixture"\n'
        f'version = "{version}"\n',
        encoding="utf-8",
    )


class ReleaseTargetTests(unittest.TestCase):
    def test_resolves_version_introduction_across_later_same_version_commits(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _git(root, "init", "-b", "main")
            _git(root, "config", "user.email", "test@example.invalid")
            _git(root, "config", "user.name", "Release Test")

            _write_version(root, "0.1.0")
            _git(root, "add", ".")
            _git(root, "commit", "-m", "v0.1.0")

            _write_version(root, "0.1.1")
            _git(root, "add", ".")
            _git(root, "commit", "-m", "v0.1.1")
            introduction = _git(root, "rev-parse", "HEAD")

            (root / "README.md").write_text("docs\n", encoding="utf-8")
            _git(root, "add", "README.md")
            _git(root, "commit", "-m", "docs")

            init_path = root / "agentic_repo_kit" / "__init__.py"
            init_path.write_text(
                '"""same-version hotfix metadata"""\n__version__ = "0.1.1"\n',
                encoding="utf-8",
            )
            _git(root, "add", str(init_path.relative_to(root)))
            _git(root, "commit", "-m", "same version hotfix")

            self.assertEqual(
                introduction,
                resolve_release_target(root, "0.1.1", "HEAD"),
            )

    def test_existing_tag_is_canonical_when_consistent(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _git(root, "init", "-b", "main")
            _git(root, "config", "user.email", "test@example.invalid")
            _git(root, "config", "user.name", "Release Test")
            _write_version(root, "0.2.0")
            _git(root, "add", ".")
            _git(root, "commit", "-m", "v0.2.0")
            tagged = _git(root, "rev-parse", "HEAD")
            _git(root, "tag", "v0.2.0")

            (root / "README.md").write_text("later\n", encoding="utf-8")
            _git(root, "add", "README.md")
            _git(root, "commit", "-m", "later docs")

            self.assertEqual(tagged, resolve_release_target(root, "0.2.0", "HEAD"))


if __name__ == "__main__":
    unittest.main()
