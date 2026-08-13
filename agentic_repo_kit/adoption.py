from __future__ import annotations

from dataclasses import dataclass
from difflib import unified_diff
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import tempfile

from . import __version__
from .config import RepositoryConfig, load_config
from .errors import AgenticRepoError
from .operations import LOCK_NAME, TRUSTED_GENERATED_PATHS
from .paths import confined_repo_path, validate_output_path
from .render import GENERATED_MARKER, render_generated_files


ADOPTION_PLAN_FORMAT = 1
_PLAN_ID = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class AdoptionInput:
    kind: str
    path: str
    sha256: str


@dataclass(frozen=True)
class AdoptionFile:
    path: str
    action: str
    current_sha256: str | None
    prospective_sha256: str
    diff: str | None


@dataclass(frozen=True)
class AdoptionPlan:
    format: int
    tool_version: str
    plan_id: str
    config_sha256: str
    inputs: tuple[AdoptionInput, ...]
    files: tuple[AdoptionFile, ...]
    operator_decisions: tuple[str, ...]

    def as_dict(self) -> dict:
        return {
            "format": self.format,
            "tool_version": self.tool_version,
            "plan_id": self.plan_id,
            "config_sha256": self.config_sha256,
            "inputs": [
                {"kind": item.kind, "path": item.path, "sha256": item.sha256}
                for item in self.inputs
            ],
            "files": [
                {
                    "path": item.path,
                    "action": item.action,
                    "current_sha256": item.current_sha256,
                    "prospective_sha256": item.prospective_sha256,
                    "diff": item.diff,
                }
                for item in self.files
            ],
            "operator_decisions": list(self.operator_decisions),
        }


def _digest_text(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()


def _read_text(path: Path, *, label: str) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise AgenticRepoError(f"{label} not found: {path}") from exc
    except IsADirectoryError as exc:
        raise AgenticRepoError(f"{label} is not a regular file: {path}") from exc
    except UnicodeDecodeError as exc:
        raise AgenticRepoError(f"{label} is not UTF-8 text: {path}") from exc


def _replacement_diff(relative: str, current: str, prospective: str) -> str:
    return "".join(
        unified_diff(
            current.splitlines(keepends=True),
            prospective.splitlines(keepends=True),
            fromfile=f"current/{relative}",
            tofile=f"prospective/{relative}",
        )
    )


def _local_inputs(config: RepositoryConfig) -> tuple[tuple[str, str], ...]:
    values: list[tuple[str, str]] = []
    for kind, paths in (
        ("policy", config.local.policy_files),
        ("playbook", config.local.playbook_files),
        ("pr", config.local.pr_files),
    ):
        values.extend((kind, path) for path in paths)
    return tuple(values)


def _canonical_plan_payload(
    *,
    config_sha256: str,
    inputs: tuple[AdoptionInput, ...],
    files: tuple[AdoptionFile, ...],
) -> bytes:
    payload = {
        "format": ADOPTION_PLAN_FORMAT,
        "tool_version": __version__,
        "config_sha256": config_sha256,
        "inputs": [
            {"kind": item.kind, "path": item.path, "sha256": item.sha256}
            for item in inputs
        ],
        "files": [
            {
                "path": item.path,
                "action": item.action,
                "current_sha256": item.current_sha256,
                "prospective_sha256": item.prospective_sha256,
            }
            for item in files
        ],
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def build_adoption_plan(root: Path, config_path: Path) -> AdoptionPlan:
    root = root.resolve()
    lock_path = validate_output_path(root, LOCK_NAME)
    if lock_path.exists():
        raise AgenticRepoError(
            f"{LOCK_NAME} already exists; this repository already has managed ownership, use upgrade instead"
        )

    config_text = _read_text(config_path, label="adoption config")
    config_sha256 = _digest_text(config_text)
    config = load_config(config_path)
    generated = render_generated_files(config, root)

    local_specs = _local_inputs(config)
    local_paths = {path for _, path in local_specs}
    overlap = sorted(local_paths & set(generated))
    if overlap:
        raise AgenticRepoError(
            "local input path overlaps a generated managed output: " + ", ".join(overlap)
        )

    roadmap = confined_repo_path(root, config.project.roadmap, label="project.roadmap")
    roadmap_text = _read_text(roadmap, label="configured roadmap")
    inputs: list[AdoptionInput] = [
        AdoptionInput(kind="roadmap", path=config.project.roadmap, sha256=_digest_text(roadmap_text))
    ]
    for kind, relative in local_specs:
        path = confined_repo_path(root, relative, label="local input")
        text = _read_text(path, label="local input")
        inputs.append(AdoptionInput(kind=kind, path=relative, sha256=_digest_text(text)))

    files: list[AdoptionFile] = []
    for relative, prospective in generated.items():
        if relative not in TRUSTED_GENERATED_PATHS and relative != LOCK_NAME:
            raise AgenticRepoError(f"renderer produced untrusted adoption output: {relative}")
        path = validate_output_path(root, relative)
        prospective_sha = _digest_text(prospective)
        if not path.exists():
            files.append(
                AdoptionFile(
                    path=relative,
                    action="create",
                    current_sha256=None,
                    prospective_sha256=prospective_sha,
                    diff=None,
                )
            )
            continue

        current = _read_text(path, label="existing contract file")
        current_sha = _digest_text(current)
        if current == prospective:
            action = "unchanged"
            diff = None
        elif GENERATED_MARKER in current and relative in TRUSTED_GENERATED_PATHS:
            action = "replace_generated_orphan"
            diff = _replacement_diff(relative, current, prospective)
        else:
            action = "replace_unmanaged"
            diff = _replacement_diff(relative, current, prospective)
        files.append(
            AdoptionFile(
                path=relative,
                action=action,
                current_sha256=current_sha,
                prospective_sha256=prospective_sha,
                diff=diff,
            )
        )

    input_tuple = tuple(inputs)
    file_tuple = tuple(files)
    plan_id = sha256(
        _canonical_plan_payload(
            config_sha256=config_sha256,
            inputs=input_tuple,
            files=file_tuple,
        )
    ).hexdigest()

    replace_unmanaged = [item.path for item in file_tuple if item.action == "replace_unmanaged"]
    decisions: list[str] = []
    if replace_unmanaged:
        decisions.append(
            "Review every replace_unmanaged diff and move any project-specific text that must survive "
            "into configured [local] fragments before applying: " + ", ".join(replace_unmanaged)
        )
    decisions.append(
        "Apply only after the reviewed plan_id still matches; any change to config, local inputs, roadmap, "
        "existing contract files, prospective output, or tool version produces a different token."
    )

    return AdoptionPlan(
        format=ADOPTION_PLAN_FORMAT,
        tool_version=__version__,
        plan_id=plan_id,
        config_sha256=config_sha256,
        inputs=input_tuple,
        files=file_tuple,
        operator_decisions=tuple(decisions),
    )


def adoption_report(plan: AdoptionPlan) -> str:
    return json.dumps(plan.as_dict(), indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _atomic_replace_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.agentic-adopt-", dir=path.parent)
    temporary_path = Path(temporary)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def apply_adoption(root: Path, config_path: Path, expected_plan_id: str) -> list[str]:
    if not _PLAN_ID.fullmatch(expected_plan_id):
        raise AgenticRepoError("adoption apply requires the exact 64-hex-character plan_id")

    plan = build_adoption_plan(root, config_path)
    if plan.plan_id != expected_plan_id:
        raise AgenticRepoError(
            f"adoption plan changed: expected {expected_plan_id}, current {plan.plan_id}; review a fresh plan"
        )

    config = load_config(config_path)
    generated = render_generated_files(config, root)
    planned = {item.path: item for item in plan.files}

    for relative, prospective in generated.items():
        item = planned[relative]
        if _digest_text(prospective) != item.prospective_sha256:
            raise AgenticRepoError(f"prospective adoption output changed after planning: {relative}")
        path = validate_output_path(root, relative)
        if item.current_sha256 is None:
            if path.exists():
                raise AgenticRepoError(f"adoption target appeared after planning: {relative}")
        else:
            current = _read_text(path, label="adoption target")
            if _digest_text(current) != item.current_sha256:
                raise AgenticRepoError(f"adoption target changed after planning: {relative}")

    changes = [item for item in plan.files if item.action != "unchanged"]
    if not changes:
        return []

    originals: dict[str, str | None] = {}
    for item in changes:
        path = validate_output_path(root, item.path)
        originals[item.path] = _read_text(path, label="adoption target") if path.exists() else None

    ordered = sorted(changes, key=lambda item: (item.path == LOCK_NAME, item.path))
    applied: list[str] = []
    try:
        for item in ordered:
            _atomic_replace_text(validate_output_path(root, item.path), generated[item.path])
            applied.append(item.path)
    except Exception as exc:
        rollback_errors: list[str] = []
        for relative in reversed(applied):
            path = validate_output_path(root, relative)
            original = originals[relative]
            try:
                if original is None:
                    if path.exists():
                        path.unlink()
                else:
                    _atomic_replace_text(path, original)
            except Exception as rollback_exc:  # pragma: no cover
                rollback_errors.append(f"{relative}: {rollback_exc}")
        detail = f"adoption apply failed and was rolled back: {exc}"
        if rollback_errors:
            detail += "; rollback failures: " + "; ".join(rollback_errors)
        raise AgenticRepoError(detail) from exc

    return applied
