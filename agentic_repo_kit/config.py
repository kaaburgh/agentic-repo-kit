from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import tomllib

from .errors import AgenticRepoError


SUPPORTED_KIT_VERSION = 1


@dataclass(frozen=True)
class ProjectConfig:
    name: str
    kind: str
    roadmap: str = "ROADMAP.md"


@dataclass(frozen=True)
class WorkflowConfig:
    cloud_first: bool = True


@dataclass(frozen=True)
class RoadmapConfig:
    """Project-tunable roadmap vocabulary and derived-metric thresholds.

    Defaults are chosen to be useful without configuration. The vocabulary is
    advisory by default so that adopting a newer kit cannot turn an existing,
    structurally valid roadmap red without a repository change; a project that
    wants the stricter contract opts in with `enforce_status_vocabulary`.
    """

    extra_statuses: tuple[str, ...] = ()
    enforce_status_vocabulary: bool = False
    ready_floor: int = 1
    ready_floor_fraction: float = 0.1
    chokepoint_fraction: float = 0.5
    record_directories: tuple[str, ...] = ()


@dataclass(frozen=True)
class LocalInputs:
    policy_files: tuple[str, ...] = ()
    playbook_files: tuple[str, ...] = ()
    pr_files: tuple[str, ...] = ()


@dataclass(frozen=True)
class RepositoryConfig:
    kit_version: int
    profiles: tuple[str, ...]
    project: ProjectConfig
    workflow: WorkflowConfig = field(default_factory=WorkflowConfig)
    roadmap: RoadmapConfig = field(default_factory=RoadmapConfig)
    local: LocalInputs = field(default_factory=LocalInputs)


def _reject_unknown(table: dict, allowed: set[str], context: str) -> None:
    unknown = sorted(set(table) - allowed)
    if unknown:
        raise AgenticRepoError(f"unknown {context} key(s): {', '.join(unknown)}")


def _table(raw: dict, key: str) -> dict:
    value = raw.get(key, {})
    if not isinstance(value, dict):
        raise AgenticRepoError(f"{key} must be a table")
    return value


def _string_list(table: dict, key: str, *, context: str = "") -> tuple[str, ...]:
    value = table.get(key, [])
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        prefix = f"{context}." if context else ""
        raise AgenticRepoError(f"{prefix}{key} must be an array of strings")
    return tuple(value)


def _fraction(table: dict, key: str, default: float) -> float:
    value = table.get(key, default)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise AgenticRepoError(f"roadmap.{key} must be a number between 0 and 1")
    value = float(value)
    if not 0.0 <= value <= 1.0:
        raise AgenticRepoError(f"roadmap.{key} must be a number between 0 and 1")
    return value


def _roadmap_config(raw: dict) -> RoadmapConfig:
    table = _table(raw, "roadmap")
    _reject_unknown(
        table,
        {
            "extra_statuses",
            "enforce_status_vocabulary",
            "ready_floor",
            "ready_floor_fraction",
            "chokepoint_fraction",
            "record_directories",
        },
        "roadmap",
    )

    extra_statuses = _string_list(table, "extra_statuses", context="roadmap")
    if any(not value.strip() for value in extra_statuses):
        raise AgenticRepoError("roadmap.extra_statuses entries must be non-empty strings")

    record_directories = _string_list(table, "record_directories", context="roadmap")
    if any(not value.strip() for value in record_directories):
        raise AgenticRepoError("roadmap.record_directories entries must be non-empty strings")
    if len(set(record_directories)) != len(record_directories):
        raise AgenticRepoError("roadmap.record_directories must not contain duplicates")

    enforce = table.get("enforce_status_vocabulary", False)
    if not isinstance(enforce, bool):
        raise AgenticRepoError("roadmap.enforce_status_vocabulary must be a boolean")

    ready_floor = table.get("ready_floor", 1)
    if not isinstance(ready_floor, int) or isinstance(ready_floor, bool) or ready_floor < 0:
        raise AgenticRepoError("roadmap.ready_floor must be a non-negative integer")

    return RoadmapConfig(
        extra_statuses=extra_statuses,
        enforce_status_vocabulary=enforce,
        ready_floor=ready_floor,
        ready_floor_fraction=_fraction(table, "ready_floor_fraction", 0.1),
        chokepoint_fraction=_fraction(table, "chokepoint_fraction", 0.5),
        record_directories=record_directories,
    )


def load_config(path: Path) -> RepositoryConfig:
    try:
        raw = tomllib.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise AgenticRepoError(f"config not found: {path}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise AgenticRepoError(f"invalid TOML in {path}: {exc}") from exc

    _reject_unknown(
        raw,
        {"kit_version", "profiles", "project", "workflow", "roadmap", "local"},
        "top-level",
    )

    kit_version = raw.get("kit_version")
    if not isinstance(kit_version, int) or isinstance(kit_version, bool) or kit_version < 1:
        raise AgenticRepoError("kit_version must be a positive integer")
    if kit_version != SUPPORTED_KIT_VERSION:
        raise AgenticRepoError(
            f"unsupported kit_version {kit_version}; this tool supports {SUPPORTED_KIT_VERSION}"
        )

    profiles = _string_list(raw, "profiles")
    if not profiles:
        raise AgenticRepoError("profiles must contain at least one profile")
    if len(set(profiles)) != len(profiles):
        raise AgenticRepoError("profiles must not contain duplicates")
    if "core" not in profiles:
        raise AgenticRepoError("profiles must explicitly include 'core'")
    if profiles[0] != "core":
        raise AgenticRepoError("'core' must be the first profile")

    project = _table(raw, "project")
    _reject_unknown(project, {"name", "kind", "roadmap"}, "project")
    name = project.get("name")
    kind = project.get("kind")
    roadmap = project.get("roadmap", "ROADMAP.md")
    if not all(isinstance(value, str) and value.strip() for value in (name, kind, roadmap)):
        raise AgenticRepoError("project.name, project.kind and project.roadmap must be non-empty strings")

    workflow_raw = _table(raw, "workflow")
    _reject_unknown(workflow_raw, {"cloud_first"}, "workflow")
    cloud_first = workflow_raw.get("cloud_first", True)
    if not isinstance(cloud_first, bool):
        raise AgenticRepoError("workflow.cloud_first must be a boolean")
    workflow = WorkflowConfig(cloud_first=cloud_first)

    local_raw = _table(raw, "local")
    _reject_unknown(local_raw, {"policy_files", "playbook_files", "pr_files"}, "local")
    local = LocalInputs(
        policy_files=_string_list(local_raw, "policy_files", context="local"),
        playbook_files=_string_list(local_raw, "playbook_files", context="local"),
        pr_files=_string_list(local_raw, "pr_files", context="local"),
    )

    return RepositoryConfig(
        kit_version=kit_version,
        profiles=profiles,
        project=ProjectConfig(name=name.strip(), kind=kind.strip(), roadmap=roadmap.strip()),
        workflow=workflow,
        roadmap=_roadmap_config(raw),
        local=local,
    )
