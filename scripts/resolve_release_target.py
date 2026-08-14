from __future__ import annotations

import argparse
from pathlib import Path
import re
import subprocess
import tomllib


_VERSION_RE = re.compile(r'__version__\s*=\s*["\']([^"\']+)["\']')


def _git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=check,
    )


def _commit_version(root: Path, sha: str) -> str | None:
    package = _git(root, "show", f"{sha}:agentic_repo_kit/__init__.py", check=False)
    project = _git(root, "show", f"{sha}:pyproject.toml", check=False)
    if package.returncode or project.returncode:
        return None
    match = _VERSION_RE.search(package.stdout)
    if match is None:
        return None
    try:
        project_version = tomllib.loads(project.stdout)["project"]["version"]
    except (tomllib.TOMLDecodeError, KeyError, TypeError):
        return None
    return match.group(1) if match.group(1) == project_version else None


def resolve_release_target(root: Path, version: str, main_ref: str) -> str:
    root = root.resolve()
    tag = f"v{version}"
    tagged = _git(root, "rev-parse", "-q", "--verify", f"refs/tags/{tag}", check=False)
    if tagged.returncode == 0:
        target = _git(root, "rev-list", "-n", "1", tag).stdout.strip()
    else:
        history = _git(root, "log", "--format=%H", "--", "agentic_repo_kit/__init__.py").stdout.splitlines()
        target = ""
        for sha in history:
            commit_version = _commit_version(root, sha)
            if commit_version == version:
                target = sha
            elif target:
                break
        if not target:
            raise RuntimeError(f"cannot resolve the commit that introduced tool version {version}")

    if _commit_version(root, target) != version:
        raise RuntimeError(f"release target {target} does not have consistent tool version {version}")
    ancestor = _git(root, "merge-base", "--is-ancestor", target, main_ref, check=False)
    if ancestor.returncode != 0:
        raise RuntimeError(f"release target {target} for {tag} is not an ancestor of {main_ref}")
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve immutable release commit for a tool version")
    parser.add_argument("--version", required=True)
    parser.add_argument("--main-ref", default="origin/main")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    print(resolve_release_target(Path(args.root), args.version, args.main_ref))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
