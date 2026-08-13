from __future__ import annotations

from dataclasses import dataclass
import json
from importlib.resources import files
from pathlib import Path
import re

from .config import RepositoryConfig, load_config
from .errors import AgenticRepoError
from .render import GENERATED_MARKER, render_generated_files


CONFIG_NAME = ".agentic-repo.toml"


@dataclass(frozen=True)
class CheckResult:
    ok: bool
    problems: tuple[str, ...]


def inspect_repository(root: Path) -> dict:
    known = {
        "readme": (root / "README.md").exists(),
        "roadmap": (root / "ROADMAP.md").exists(),
        "agents": (root / "AGENTS.md").exists(),
        "claude": (root / "CLAUDE.md").exists(),
        "copilot": (root / ".github/copilot-instructions.md").exists(),
        "pr_template": (root / ".github/pull_request_template.md").exists(),
        "github_actions": (root / ".github/workflows").is_dir(),
        "agentic_config": (root / CONFIG_NAME).exists(),
    }
    extensions: dict[str, int] = {}
    ignored_dirs = {".git", ".venv", "venv", "node_modules", "build", "dist", "__pycache__", ".pytest_cache"}
    for path in root.rglob("*"):
        if (
            not path.is_file()
            or any(part in ignored_dirs for part in path.parts)
            or any(part.endswith(".egg-info") for part in path.parts)
        ):
            continue
        suffix = path.suffix.lower()
        if suffix:
            extensions[suffix] = extensions.get(suffix, 0) + 1
    return {"root": str(root.resolve()), "signals": known, "extensions": dict(sorted(extensions.items()))}


def _write_generated(root: Path, generated: dict[str, str], *, force: bool, upgrade: bool) -> list[str]:
    changed: list[str] = []
    for relative, content in generated.items():
        path = root / relative
        if path.exists():
            current = path.read_text(encoding="utf-8")
            if current == content:
                continue
            managed = relative == ".agentic-repo.lock.json" or GENERATED_MARKER in current
            if not force and not (upgrade and managed):
                raise AgenticRepoError(
                    f"refusing to overwrite unmanaged or drifted file: {relative}; "
                    "move project-specific text to [local] inputs or pass --force intentionally"
                )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        changed.append(relative)
    return changed


def bootstrap(root: Path, config_path: Path, *, force: bool = False) -> list[str]:
    config = load_config(config_path)
    generated = render_generated_files(config, root)
    return _write_generated(root, generated, force=force, upgrade=False)


def upgrade(root: Path, config_path: Path) -> list[str]:
    config = load_config(config_path)
    generated = render_generated_files(config, root)
    return _write_generated(root, generated, force=False, upgrade=True)


def _markdown_link_problems(root: Path, paths: list[Path]) -> list[str]:
    pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    problems: list[str] = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        for target in pattern.findall(text):
            target = target.split("#", 1)[0]
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            resolved = (path.parent / target).resolve()
            try:
                resolved.relative_to(root.resolve())
            except ValueError:
                problems.append(f"{path.relative_to(root)}: link escapes repository: {target}")
                continue
            if not resolved.exists():
                problems.append(f"{path.relative_to(root)}: missing relative link target: {target}")
    return problems


def check(root: Path, config_path: Path) -> CheckResult:
    config = load_config(config_path)
    problems: list[str] = []
    roadmap = root / config.project.roadmap
    if not roadmap.is_file():
        problems.append(f"roadmap not found: {config.project.roadmap}")

    expected = render_generated_files(config, root)
    markdown_paths: list[Path] = []
    for relative, content in expected.items():
        path = root / relative
        if not path.exists():
            problems.append(f"generated file missing: {relative}")
            continue
        if path.read_text(encoding="utf-8") != content:
            problems.append(f"generated file drift: {relative}")
        if path.suffix.lower() == ".md":
            markdown_paths.append(path)

    if roadmap.is_file():
        markdown_paths.append(roadmap)
    problems.extend(_markdown_link_problems(root, markdown_paths))
    return CheckResult(ok=not problems, problems=tuple(problems))


def roadmap_normalization_packet(root: Path, config: RepositoryConfig) -> str:
    skill = files("agentic_repo_kit").joinpath("skills", "normalize-roadmap.md").read_text(encoding="utf-8")
    inspection = json.dumps(inspect_repository(root), indent=2, sort_keys=True)
    return (
        f"# Roadmap normalization packet for {config.project.name}\n\n"
        f"Project kind: `{config.project.kind}`\n\n"
        f"Roadmap: `{config.project.roadmap}`\n\n"
        f"Profiles: `{', '.join(config.profiles)}`\n\n"
        "## Repository inspection\n\n"
        f"```json\n{inspection}\n```\n\n"
        "## Agent procedure\n\n"
        f"{skill.strip()}\n"
    )
