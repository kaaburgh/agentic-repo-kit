from __future__ import annotations

from pathlib import Path

from .errors import AgenticRepoError


def confined_repo_path(root: Path, relative: str, *, label: str) -> Path:
    rel = Path(relative)
    if not relative or rel.is_absolute():
        raise AgenticRepoError(f"{label} must be a non-empty repository-relative path: {relative!r}")
    if any(part == ".." for part in rel.parts):
        raise AgenticRepoError(f"{label} escapes repository: {relative}")

    base = root.resolve()
    current = base
    for part in rel.parts:
        current = current / part
        if current.is_symlink():
            raise AgenticRepoError(f"{label} uses symlinked path component: {relative}")

    resolved = (base / rel).resolve(strict=False)
    try:
        resolved.relative_to(base)
    except ValueError as exc:
        raise AgenticRepoError(f"{label} escapes repository: {relative}") from exc
    return base / rel


def validate_output_path(root: Path, relative: str) -> Path:
    path = confined_repo_path(root, relative, label="generated output")
    base = root.resolve()
    current = base
    for part in Path(relative).parts[:-1]:
        current = current / part
        if current.exists() and not current.is_dir():
            raise AgenticRepoError(f"generated output parent is not a directory: {relative}")
    if path.exists() and not path.is_file():
        raise AgenticRepoError(f"generated output is not a regular file: {relative}")
    return path
