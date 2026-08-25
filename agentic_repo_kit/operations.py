from __future__ import annotations

from dataclasses import dataclass
import json
from importlib.resources import files
from pathlib import Path
import re

from .config import RepositoryConfig, load_config
from .errors import AgenticRepoError
from .paths import confined_repo_path, validate_output_path
from .render import GENERATED_MARKER, render_generated_files
from .roadmap import analyze_roadmap, build_roadmap_graph


CONFIG_NAME = ".agentic-repo.toml"
LOCK_NAME = ".agentic-repo.lock.json"

# This allowlist is code-owned. The checkout lock may describe prior generated
# state, but it is never trusted to establish ownership of an arbitrary path.
TRUSTED_GENERATED_PATHS = frozenset(
    {
        "AGENTS.md",
        "CLAUDE.md",
        ".github/copilot-instructions.md",
        ".github/pull_request_template.md",
        ".github/workflows/agentic-repo-check.yml",
        "docs/agent-playbook.md",
        "docs/agent-cycle-run.md",
        "docs/roadmap-authoring.md",
        "docs/re/README.md",
        "docs/experiments/README.md",
    }
)


@dataclass(frozen=True)
class CheckResult:
    """Contract verdict plus the advisory planning signal derived alongside it.

    Only `problems` decides `ok`. Metrics and warnings describe the shape of a
    roadmap that is structurally valid, and must never fail the check: a check
    people learn to work around stops protecting anything.
    """

    ok: bool
    problems: tuple[str, ...]
    warnings: tuple[str, ...] = ()
    metrics: tuple[str, ...] = ()


@dataclass(frozen=True)
class _WritePlan:
    relative: str
    path: Path
    content: str


@dataclass(frozen=True)
class _DeletePlan:
    relative: str
    path: Path


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


def _validate_generated_manifest_paths(generated: dict[str, str]) -> None:
    untrusted = sorted(set(generated) - TRUSTED_GENERATED_PATHS)
    if untrusted:
        raise AgenticRepoError(
            f"previous generated manifest contains untrusted path(s): {', '.join(untrusted)}"
        )


def _load_previous_generated(root: Path) -> dict[str, str]:
    path = validate_output_path(root, LOCK_NAME)
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AgenticRepoError(f"cannot read previous generated manifest: {LOCK_NAME}") from exc
    if not isinstance(raw, dict):
        raise AgenticRepoError(f"invalid previous generated manifest: {LOCK_NAME}")
    generated = raw.get("generated")
    if not isinstance(generated, dict) or not all(
        isinstance(relative, str) and isinstance(digest, str) for relative, digest in generated.items()
    ):
        raise AgenticRepoError(f"invalid previous generated manifest: {LOCK_NAME}")
    result = dict(generated)
    _validate_generated_manifest_paths(result)
    return result


def _is_managed(relative: str, current: str) -> bool:
    if relative == LOCK_NAME:
        return True
    return relative in TRUSTED_GENERATED_PATHS and GENERATED_MARKER in current


def _preflight_generated(
    root: Path,
    generated: dict[str, str],
    *,
    force: bool,
    upgrade: bool,
    previous_generated: dict[str, str],
) -> tuple[list[_WritePlan], list[_DeletePlan]]:
    unexpected_outputs = sorted(set(generated) - TRUSTED_GENERATED_PATHS - {LOCK_NAME})
    if unexpected_outputs:
        raise AgenticRepoError(
            f"renderer produced untrusted output path(s): {', '.join(unexpected_outputs)}"
        )

    writes: list[_WritePlan] = []
    for relative, content in generated.items():
        path = validate_output_path(root, relative)
        if path.exists():
            current = path.read_text(encoding="utf-8")
            if current == content:
                continue
            managed = _is_managed(relative, current)
            if not force and not (upgrade and managed):
                raise AgenticRepoError(
                    f"refusing to overwrite unmanaged or drifted file: {relative}; "
                    "move project-specific text to [local] inputs or pass --force intentionally"
                )
        writes.append(_WritePlan(relative=relative, path=path, content=content))

    deletes: list[_DeletePlan] = []
    if upgrade:
        obsolete = sorted(set(previous_generated) - set(generated))
        for relative in obsolete:
            path = validate_output_path(root, relative)
            if not path.exists():
                continue
            current = path.read_text(encoding="utf-8")
            if not _is_managed(relative, current):
                raise AgenticRepoError(f"refusing to remove unmanaged obsolete generated file: {relative}")
            deletes.append(_DeletePlan(relative=relative, path=path))
    return writes, deletes


def _write_generated(
    root: Path,
    generated: dict[str, str],
    *,
    force: bool,
    upgrade: bool,
    previous_generated: dict[str, str] | None = None,
) -> list[str]:
    writes, deletes = _preflight_generated(
        root,
        generated,
        force=force,
        upgrade=upgrade,
        previous_generated=previous_generated or {},
    )

    changed: list[str] = []
    for plan in deletes:
        plan.path.unlink()
        changed.append(plan.relative)
    for plan in writes:
        plan.path.parent.mkdir(parents=True, exist_ok=True)
        plan.path.write_text(plan.content, encoding="utf-8")
        changed.append(plan.relative)
    return changed


def bootstrap(root: Path, config_path: Path, *, force: bool = False) -> list[str]:
    config = load_config(config_path)
    generated = render_generated_files(config, root)
    return _write_generated(root, generated, force=force, upgrade=False)


def upgrade(root: Path, config_path: Path) -> list[str]:
    config = load_config(config_path)
    previous_generated = _load_previous_generated(root)
    generated = render_generated_files(config, root)
    return _write_generated(
        root,
        generated,
        force=False,
        upgrade=True,
        previous_generated=previous_generated,
    )


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
    try:
        roadmap = confined_repo_path(root, config.project.roadmap, label="project.roadmap")
    except AgenticRepoError as exc:
        return CheckResult(ok=False, problems=(str(exc),))
    if not roadmap.is_file():
        problems.append(f"roadmap not found: {config.project.roadmap}")

    try:
        expected = render_generated_files(config, root)
    except AgenticRepoError as exc:
        problems.append(str(exc))
        return CheckResult(ok=False, problems=tuple(problems))

    markdown_paths: list[Path] = []
    for relative, content in expected.items():
        try:
            path = validate_output_path(root, relative)
        except AgenticRepoError as exc:
            problems.append(str(exc))
            continue
        if not path.exists():
            problems.append(f"generated file missing: {relative}")
            continue
        if path.read_text(encoding="utf-8") != content:
            problems.append(f"generated file drift: {relative}")
        if path.suffix.lower() == ".md":
            markdown_paths.append(path)

    warnings: list[str] = []
    metrics: list[str] = []
    if roadmap.is_file():
        roadmap_text = roadmap.read_text(encoding="utf-8")
        markdown_paths.append(roadmap)
        graph = build_roadmap_graph(roadmap_text, path=str(roadmap.relative_to(root)))
        problems.extend(graph.problems)
        analysis = analyze_roadmap(graph, config.roadmap)
        problems.extend(analysis.problems)
        warnings.extend(analysis.warnings)
        metrics.extend(analysis.metrics)
    problems.extend(_markdown_link_problems(root, markdown_paths))
    return CheckResult(
        ok=not problems,
        problems=tuple(problems),
        warnings=tuple(warnings),
        metrics=tuple(metrics),
    )


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
