from __future__ import annotations

from dataclasses import dataclass
import re


_ITEM_HEADING = re.compile(r"^(#{2,4})\s+([A-Za-z][A-Za-z0-9._-]*)\s+(?:—|--|-)\s+(.+?)\s*$")
_ANY_HEADING = re.compile(r"^(#{1,6})\s+")
_FIELD = re.compile(r"^- \*\*([^*]+):\*\*\s*(.*?)\s*$")
_LINKED_DEP_ID = re.compile(r"^\[([A-Za-z][A-Za-z0-9._-]*)\]\([^)]*\)(?:\s+\([^)]*\))?$")
_PLAIN_DEP_ID = re.compile(r"^([A-Za-z][A-Za-z0-9._-]*)(?:\s+\([^)]*\))?$")
_NO_DEPENDENCIES = {"none", "n/a", "na", "—", "-"}


@dataclass(frozen=True)
class RoadmapItem:
    item_id: str
    title: str
    line: int
    heading_level: int
    fields: dict[str, str]
    duplicate_fields: tuple[str, ...] = ()


def _normalize_field_name(raw: str) -> str:
    return " ".join(raw.strip().lower().split())


def _field_matches(item: RoadmapItem, semantic_name: str) -> tuple[tuple[str, str], ...]:
    """Return fields whose slash-separated label contains the requested semantic field."""

    semantic_name = _normalize_field_name(semantic_name)
    matches: list[tuple[str, str]] = []
    for name, value in item.fields.items():
        components = {_normalize_field_name(part) for part in name.split("/")}
        if semantic_name in components:
            matches.append((name, value))
    return tuple(matches)


def parse_structured_items(text: str) -> tuple[RoadmapItem, ...]:
    """Parse normalized roadmap items without interpreting their prose.

    Item headings at levels 2-4 are accepted because existing dogfood uses both
    `## ID — Title` and `### ID — Title`. A non-item heading at the same or a
    higher level closes the current item; deeper headings stay inside its prose.
    """

    items: list[RoadmapItem] = []
    current_id: str | None = None
    current_title = ""
    current_line = 0
    current_level = 0
    current_fields: dict[str, str] = {}
    current_duplicate_fields: list[str] = []

    def flush() -> None:
        nonlocal current_id, current_title, current_line, current_level
        nonlocal current_fields, current_duplicate_fields
        if current_id is not None:
            items.append(
                RoadmapItem(
                    item_id=current_id,
                    title=current_title,
                    line=current_line,
                    heading_level=current_level,
                    fields=dict(current_fields),
                    duplicate_fields=tuple(current_duplicate_fields),
                )
            )
        current_id = None
        current_title = ""
        current_line = 0
        current_level = 0
        current_fields = {}
        current_duplicate_fields = []

    for lineno, line in enumerate(text.splitlines(), start=1):
        heading = _ITEM_HEADING.match(line)
        if heading:
            flush()
            current_level = len(heading.group(1))
            current_id = heading.group(2)
            current_title = heading.group(3)
            current_line = lineno
            continue

        any_heading = _ANY_HEADING.match(line)
        if current_id is not None and any_heading and len(any_heading.group(1)) <= current_level:
            flush()
            continue

        if current_id is None:
            continue
        field = _FIELD.match(line)
        if field:
            name = _normalize_field_name(field.group(1))
            if name in current_fields:
                current_duplicate_fields.append(name)
            else:
                current_fields[name] = field.group(2).strip()

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

        if token.startswith("`") and token.endswith("`") and len(token) > 2:
            token = token[1:-1].strip()
        if token.startswith("**") and token.endswith("**") and len(token) > 4:
            token = token[2:-2].strip()

        linked = _LINKED_DEP_ID.match(token)
        plain = _PLAIN_DEP_ID.match(token)
        match = linked or plain
        if not match:
            malformed.append(part.strip())
            continue
        dependencies.append(match.group(1))
    return tuple(dependencies), tuple(malformed)


def structured_roadmap_problems(text: str, *, path: str = "ROADMAP.md") -> tuple[str, ...]:
    """Validate stable graph invariants for an already-normalized roadmap.

    A milestone sketch with no structured ID headings is intentionally ignored:
    semantic normalization is a separate workflow and bootstrap/check must not
    make old planning documents invalid before that pass happens. Once at least
    one structured item exists, IDs/dependencies are validated fail-closed.
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

        for duplicate in item.duplicate_fields:
            problems.append(
                f"{path}:{item.line}: structured item {item.item_id} repeats field **{duplicate}:**"
            )

    graph: dict[str, tuple[str, ...]] = {}
    for item in items:
        if by_id.get(item.item_id) is not item:
            continue

        status_fields = _field_matches(item, "status")
        if not status_fields or not status_fields[0][1].strip():
            problems.append(f"{path}:{item.line}: structured item {item.item_id} is missing **Status:**")
        elif len(status_fields) > 1:
            labels = ", ".join(name for name, _ in status_fields)
            problems.append(
                f"{path}:{item.line}: structured item {item.item_id} has multiple status fields: {labels}"
            )

        depends_fields = _field_matches(item, "depends on")
        if not depends_fields or not depends_fields[0][1].strip():
            problems.append(f"{path}:{item.line}: structured item {item.item_id} is missing **Depends on:**")
            graph[item.item_id] = ()
            continue
        if len(depends_fields) > 1:
            labels = ", ".join(name for name, _ in depends_fields)
            problems.append(
                f"{path}:{item.line}: structured item {item.item_id} has multiple dependency fields: {labels}"
            )
            graph[item.item_id] = ()
            continue

        dependencies, malformed = _dependency_ids(depends_fields[0][1])
        for token in malformed:
            problems.append(
                f"{path}:{item.line}: structured item {item.item_id} has malformed dependency {token!r}; "
                "use comma/semicolon-separated roadmap item IDs or `none`"
            )
        graph[item.item_id] = dependencies

    for item_id, dependencies in graph.items():
        item = by_id[item_id]
        for dependency in dependencies:
            if dependency == item_id:
                problems.append(f"{path}:{item.line}: structured item {item_id} depends on itself")
            elif dependency not in by_id:
                problems.append(
                    f"{path}:{item.line}: structured item {item_id} depends on unknown item {dependency}"
                )

    state: dict[str, int] = {}
    stack: list[str] = []
    reported_edges: set[tuple[str, str]] = set()

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
                edge = (item_id, dependency)
                if edge not in reported_edges:
                    reported_edges.add(edge)
                    start = stack.index(dependency)
                    cycle = stack[start:] + [dependency]
                    item = by_id[item_id]
                    problems.append(
                        f"{path}:{item.line}: roadmap dependency cycle: {' -> '.join(cycle)}"
                    )
        stack.pop()
        state[item_id] = 2

    for item_id in by_id:
        if state.get(item_id, 0) == 0:
            visit(item_id)

    return tuple(problems)
