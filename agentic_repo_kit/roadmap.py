from __future__ import annotations

from dataclasses import dataclass
import re


_ITEM_HEADING = re.compile(r"^###\s+([A-Za-z][A-Za-z0-9._-]*)\s+(?:—|--|-)\s+(.+?)\s*$")
_FIELD = re.compile(r"^- \*\*([^*]+):\*\*\s*(.*?)\s*$")
_DEP_ID = re.compile(r"^\[?([A-Za-z][A-Za-z0-9._-]*)\]?(?:\([^)]*\))?(?:\s+\([^)]*\))?$")
_NO_DEPENDENCIES = {"none", "n/a", "na", "—", "-"}


@dataclass(frozen=True)
class RoadmapItem:
    item_id: str
    title: str
    line: int
    fields: dict[str, str]


def parse_structured_items(text: str) -> tuple[RoadmapItem, ...]:
    """Parse normalized `### ID — Title` roadmap items without interpreting prose."""

    items: list[RoadmapItem] = []
    current_id: str | None = None
    current_title = ""
    current_line = 0
    current_fields: dict[str, str] = {}

    def flush() -> None:
        nonlocal current_id, current_title, current_line, current_fields
        if current_id is not None:
            items.append(
                RoadmapItem(
                    item_id=current_id,
                    title=current_title,
                    line=current_line,
                    fields=dict(current_fields),
                )
            )
        current_id = None
        current_title = ""
        current_line = 0
        current_fields = {}

    for lineno, line in enumerate(text.splitlines(), start=1):
        heading = _ITEM_HEADING.match(line)
        if heading:
            flush()
            current_id = heading.group(1)
            current_title = heading.group(2)
            current_line = lineno
            continue
        if current_id is None:
            continue
        field = _FIELD.match(line)
        if field:
            current_fields[field.group(1).strip().lower()] = field.group(2).strip()

    flush()
    return tuple(items)


def _dependency_ids(raw: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
    value = raw.strip()
    if value.lower() in _NO_DEPENDENCIES:
        return (), ()

    dependencies: list[str] = []
    malformed: list[str] = []
    for part in re.split(r"[,;]", value):
        token = part.strip()
        if not token:
            malformed.append("<empty>")
            continue
        match = _DEP_ID.match(token)
        if not match:
            malformed.append(token)
            continue
        dependencies.append(match.group(1))
    return tuple(dependencies), tuple(malformed)


def structured_roadmap_problems(text: str, *, path: str = "ROADMAP.md") -> tuple[str, ...]:
    """Validate stable graph invariants for an already-normalized roadmap.

    A milestone sketch with no `### ID — Title` items is intentionally ignored: semantic
    normalization is a separate workflow and bootstrap/check must not make old planning
    documents invalid before that pass happens.
    """

    items = parse_structured_items(text)
    if not items:
        return ()

    problems: list[str] = []
    by_id: dict[str, RoadmapItem] = {}
    for item in items:
        previous = by_id.get(item.item_id)
        if previous is not None:
            problems.append(
                f"{path}:{item.line}: duplicate roadmap item id {item.item_id!r}; "
                f"first declared at line {previous.line}"
            )
            continue
        by_id[item.item_id] = item

    graph: dict[str, tuple[str, ...]] = {}
    for item in items:
        if by_id.get(item.item_id) is not item:
            continue
        status = item.fields.get("status")
        if not status:
            problems.append(f"{path}:{item.line}: structured item {item.item_id} is missing **Status:**")

        depends_raw = item.fields.get("depends on")
        if depends_raw is None or not depends_raw.strip():
            problems.append(f"{path}:{item.line}: structured item {item.item_id} is missing **Depends on:**")
            graph[item.item_id] = ()
            continue

        dependencies, malformed = _dependency_ids(depends_raw)
        for token in malformed:
            problems.append(
                f"{path}:{item.line}: structured item {item.item_id} has malformed dependency {token!r}; "
                "use comma/semicolon-separated roadmap item IDs or `none`"
            )
        graph[item.item_id] = dependencies

    for item_id, dependencies in graph.items():
        for dependency in dependencies:
            if dependency == item_id:
                problems.append(f"{path}: structured item {item_id} depends on itself")
            elif dependency not in by_id:
                problems.append(f"{path}: structured item {item_id} depends on unknown item {dependency}")

    state: dict[str, int] = {}
    stack: list[str] = []
    reported_cycles: set[tuple[str, ...]] = set()

    def visit(item_id: str) -> None:
        state[item_id] = 1
        stack.append(item_id)
        for dependency in graph.get(item_id, ()):
            if dependency not in by_id or dependency == item_id:
                continue
            dep_state = state.get(dependency, 0)
            if dep_state == 0:
                visit(dependency)
            elif dep_state == 1:
                start = stack.index(dependency)
                cycle = tuple(stack[start:] + [dependency])
                if cycle not in reported_cycles:
                    reported_cycles.add(cycle)
                    problems.append(f"{path}: roadmap dependency cycle: {' -> '.join(cycle)}")
        stack.pop()
        state[item_id] = 2

    for item_id in by_id:
        if state.get(item_id, 0) == 0:
            visit(item_id)

    return tuple(problems)
