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
    roadmap_driven: bool = True
    one_roadmap_item_per_pr: bool = True


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
    local: LocalInputs = field(default_factory=LocalInputs)


def _string_list(table: dict, key: str) -> tuple[str, ...]:
    value = table.get(key, [])
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise AgenticRepoError(f"{key} must be an array of strings")
    return tuple(value)


def load_config(path: Path) -> RepositoryConfig:
    try:
        raw = tomllib.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise AgenticRepoError(f"config not found: {path}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise AgenticRepoError(f"invalid TOML in {path}: {exc}") from exc

    kit_version = raw.get("kit_version")
    if not isinstance(kit_version, int) or kit_version < 1:
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

    project = raw.get("project", {})
    name = project.get("name")
    kind = project.get("kind")
    roadmap = project.get("roadmap", "ROADMAP.md")
    if not all(isinstance(value, str) and value.strip() for value in (name, kind, roadmap)):
        raise AgenticRepoError("project.name, project.kind and project.roadmap must be non-empty strings")

    workflow_raw = raw.get("workflow", {})

    def workflow_bool(key: str, default: bool) -> bool:
        value = workflow_raw.get(key, default)
        if not isinstance(value, bool):
            raise AgenticRepoError(f"workflow.{key} must be a boolean")
        return value

    workflow = WorkflowConfig(
        cloud_first=workflow_bool("cloud_first", True),
        roadmap_driven=workflow_bool("roadmap_driven", True),
        one_roadmap_item_per_pr=workflow_bool("one_roadmap_item_per_pr", True),
    )

    local_raw = raw.get("local", {})
    local = LocalInputs(
        policy_files=_string_list(local_raw, "policy_files"),
        playbook_files=_string_list(local_raw, "playbook_files"),
        pr_files=_string_list(local_raw, "pr_files"),
    )

    return RepositoryConfig(
        kit_version=kit_version,
        profiles=profiles,
        project=ProjectConfig(name=name.strip(), kind=kind.strip(), roadmap=roadmap.strip()),
        workflow=workflow,
        local=local,
    )
