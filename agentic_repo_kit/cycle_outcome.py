from __future__ import annotations

import re

from .config import RoadmapConfig
from .roadmap import RoadmapGraph, RoadmapItem, read_status


CYCLE_OUTCOME_STATUSES = frozenset({"Investigation first", "Partially implemented"})
_SIMPLE_OUTCOMES = frozenset({"evidence", "durable negative", "operator handoff"})
_TOOLING_OUTCOME = re.compile(
    r"^tooling only\s*\(\s*(unknown|[1-9][0-9]*)\s*\)\s*(?:—|--|-)\s*(\S(?:.*\S)?)$",
    re.IGNORECASE,
)


def _normalize_field_name(raw: str) -> str:
    return " ".join(raw.strip().lower().split())


def _cycle_outcome_fields(item: RoadmapItem) -> tuple[tuple[str, str], ...]:
    matches: list[tuple[str, str]] = []
    for name, value in item.fields.items():
        components = {_normalize_field_name(part) for part in name.split("/")}
        if "cycle outcome" in components:
            matches.append((name, value))
    return tuple(matches)


def _outcome_problem(value: str) -> str | None:
    normalized = " ".join(value.strip().lower().split())
    if normalized in _SIMPLE_OUTCOMES:
        return None
    if _TOOLING_OUTCOME.fullmatch(value.strip()) is not None:
        return None
    return (
        "use `evidence`, `durable negative`, `operator handoff`, or "
        "`tooling only (<positive integer>|unknown) — <remaining step>`"
    )


def cycle_outcome_warnings(graph: RoadmapGraph, config: RoadmapConfig) -> tuple[str, ...]:
    """Return advisory warnings for the durable per-item cycle outcome field.

    The field records the latest durable result for work that commonly spans
    cycles. Its syntax is mechanically checkable; continuity of a tooling-only
    streak is not, because overwriting the field removes the previous value.
    The unattended runner must read the predecessor before writing the next
    outcome and preserve provenance for that transition.
    """

    warnings: list[str] = []
    for item in graph.items:
        reading = read_status(item, extra_statuses=config.extra_statuses)
        if reading is None or reading.canonical not in CYCLE_OUTCOME_STATUSES:
            continue

        fields = _cycle_outcome_fields(item)
        if not fields or not fields[0][1].strip():
            warnings.append(
                f"{graph.path}:{item.line}: structured item {item.item_id} is "
                f"'{reading.canonical}' without **Cycle outcome:**; record the latest durable "
                "cycle result so a later cycle can read a real predecessor"
            )
            continue
        if len(fields) > 1:
            labels = ", ".join(name for name, _ in fields)
            warnings.append(
                f"{graph.path}:{item.line}: structured item {item.item_id} has multiple "
                f"cycle-outcome fields: {labels}; use one standalone **Cycle outcome:** field"
            )
            continue

        label, value = fields[0]
        if _normalize_field_name(label) != "cycle outcome":
            warnings.append(
                f"{graph.path}:{item.line}: structured item {item.item_id} declares cycle outcome "
                f"inside compact field **{label}:**; use a standalone **Cycle outcome:** field"
            )
            continue

        problem = _outcome_problem(value)
        if problem is not None:
            warnings.append(
                f"{graph.path}:{item.line}: structured item {item.item_id} has malformed "
                f"**Cycle outcome:** {value!r}; {problem}"
            )

    return tuple(warnings)
