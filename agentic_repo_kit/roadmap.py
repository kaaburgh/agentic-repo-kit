from __future__ import annotations

from dataclasses import dataclass
import re

from .config import RoadmapConfig


_ITEM_HEADING = re.compile(r"^(#{2,4})\s+([A-Za-z][A-Za-z0-9._-]*)\s+(?:—|--|-)\s+(.+?)\s*$")
_ANY_HEADING = re.compile(r"^(#{1,6})\s+")
_FIELD = re.compile(r"^- \*\*([^*]+):\*\*\s*(.*?)\s*$")
_FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
_ID = r"[A-Za-z][A-Za-z0-9._-]*"
_LINKED_DEP_ID = re.compile(rf"^\[({_ID})\]\([^)]*\)(?:\s+\([^)]*\))?$")
_CODE_DEP_ID = re.compile(rf"^`({_ID})`(?:\s+\([^)]*\))?$")
_BOLD_DEP_ID = re.compile(rf"^\*\*({_ID})\*\*(?:\s+\([^)]*\))?$")
_PLAIN_DEP_ID = re.compile(rf"^({_ID})(?:\s+\([^)]*\))?$")
_NO_DEPENDENCIES = {"none", "n/a", "na", "—", "-"}


@dataclass(frozen=True)
class RoadmapItem:
    item_id: str
    title: str
    line: int
    heading_level: int
    fields: dict[str, str]
    duplicate_fields: tuple[str, ...] = ()


@dataclass(frozen=True)
class RoadmapGraph:
    """A parsed roadmap plus the dependency edges its validation resolved."""

    path: str
    items: tuple[RoadmapItem, ...]
    dependencies: dict[str, tuple[str, ...]]
    problems: tuple[str, ...]


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

    Existing dogfood uses both `## ID — Title` and `### ID — Title`. Fieldless
    headings are retained as broken items once the document is structured, except
    for a specific heading that demonstrably contains deeper field-bearing items
    and therefore acts as a section container. If the document has no field-bearing
    candidates at all, it remains a pre-normalization milestone sketch and returns
    no items.

    Fenced Markdown examples are ignored so a documented item schema cannot
    create phantom graph nodes.
    """

    candidates: list[RoadmapItem] = []
    current_id: str | None = None
    current_title = ""
    current_line = 0
    current_level = 0
    current_fields: dict[str, str] = {}
    current_duplicate_fields: list[str] = []
    fence_char: str | None = None
    fence_length = 0

    def flush() -> None:
        nonlocal current_id, current_title, current_line, current_level
        nonlocal current_fields, current_duplicate_fields
        if current_id is not None:
            candidates.append(
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
        fence = _FENCE.match(line)
        if fence_char is not None:
            if fence and fence.group(1)[0] == fence_char and len(fence.group(1)) >= fence_length:
                fence_char = None
                fence_length = 0
            continue
        if fence:
            marker = fence.group(1)
            fence_char = marker[0]
            fence_length = len(marker)
            continue

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

    if not any(item.fields for item in candidates):
        return ()

    section_lines: set[int] = set()
    for index, item in enumerate(candidates):
        if item.fields:
            continue
        for child in candidates[index + 1 :]:
            if child.heading_level <= item.heading_level:
                break
            if child.fields:
                section_lines.add(item.line)
                break

    return tuple(
        item
        for item in candidates
        if item.fields or item.line not in section_lines
    )


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

        match = (
            _LINKED_DEP_ID.match(token)
            or _CODE_DEP_ID.match(token)
            or _BOLD_DEP_ID.match(token)
            or _PLAIN_DEP_ID.match(token)
        )
        if not match:
            malformed.append(token)
            continue
        dependencies.append(match.group(1))
    return tuple(dependencies), tuple(malformed)


def build_roadmap_graph(text: str, *, path: str = "ROADMAP.md") -> RoadmapGraph:
    """Parse a normalized roadmap once and validate its stable graph invariants.

    A milestone sketch with no structured ID items is intentionally ignored:
    semantic normalization is a separate workflow and bootstrap/check must not
    make old planning documents invalid before that pass happens. Once at least
    one structured item exists, IDs/dependencies are validated fail-closed.

    The parsed items and the resolved dependency edges are returned alongside the
    problems so derived planning metrics consume exactly the graph that was
    validated, instead of re-deriving a second one that can disagree with it.
    """

    items = parse_structured_items(text)
    if not items:
        return RoadmapGraph(path=path, items=(), dependencies={}, problems=())

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

    return RoadmapGraph(
        path=path,
        items=tuple(by_id.values()),
        dependencies=graph,
        problems=tuple(problems),
    )


def structured_roadmap_problems(text: str, *, path: str = "ROADMAP.md") -> tuple[str, ...]:
    """Return only the fail-closed graph problems for a normalized roadmap."""

    return build_roadmap_graph(text, path=path).problems


_STATUS_BLOCKED_TEMPLATE = "Blocked (<ID>)"
_BLOCKED_ON_ITEM = re.compile(rf"^blocked\s*\(\s*({_ID})\s*\)$", re.IGNORECASE)
_SLICE_BUDGET = re.compile(r"^(\d+)\s*/\s*(\d+)$")

WORKABLE_STATUSES = (
    "Open",
    "Investigation first",
    "Partially implemented",
    "Implemented, validation incomplete",
)
SATISFYING_STATUSES = (
    "Completed (contract scope)",
    "Completed and verified",
)
CANONICAL_STATUSES = (
    "Open",
    "Investigation first",
    "Blocked on target evidence",
    _STATUS_BLOCKED_TEMPLATE,
    "Partially implemented",
    "Implemented, validation incomplete",
    "Completed (contract scope)",
    "Completed and verified",
    "Superseded",
    "Dropped",
)
SLICE_BUDGET_STATUS = "Partially implemented"

_LITERAL_STATUSES = {
    status.lower(): status for status in CANONICAL_STATUSES if status != _STATUS_BLOCKED_TEMPLATE
}
_CLOSED_STATUSES = frozenset(SATISFYING_STATUSES) | {"Superseded", "Dropped"}
_WORKABLE = frozenset(status.lower() for status in WORKABLE_STATUSES)
_SATISFYING = frozenset(status.lower() for status in SATISFYING_STATUSES)


def _normalize_status(raw: str) -> str:
    return " ".join(raw.strip().lower().split())


@dataclass(frozen=True)
class StatusReading:
    """One item's status, read from a standalone or compact status field.

    `canonical` is the shipped spelling for a recognized status, a configured
    project extension, or `None` when the value is outside the vocabulary. A
    project extension is a valid value but is deliberately neither workable nor
    dependency-satisfying: only the shipped vocabulary carries those semantics.
    """

    label: str
    value: str
    canonical: str | None = None
    blocker: str | None = None
    problem: str | None = None

    @property
    def is_workable(self) -> bool:
        return self.canonical is not None and self.canonical.lower() in _WORKABLE

    @property
    def is_satisfying(self) -> bool:
        return self.canonical is not None and self.canonical.lower() in _SATISFYING


def _status_component(label: str, value: str) -> tuple[str | None, str | None]:
    """Read the status out of a possibly compact slash-separated field.

    A compact label such as `Status / priority / execution` carries its value
    positionally, so membership must be tested against the status component
    rather than the whole value.
    """

    components = [_normalize_field_name(part) for part in label.split("/")]
    if len(components) == 1:
        return value.strip(), None
    parts = [part.strip() for part in value.split("/")]
    if len(parts) != len(components):
        return None, (
            f"a compact status field **{label}:** carrying {len(components)} labels but "
            f"{len(parts)} value component(s), so its status cannot be read positionally"
        )
    return parts[components.index("status")], None


def read_status(item: RoadmapItem, *, extra_statuses: tuple[str, ...] = ()) -> StatusReading | None:
    """Return the item's status reading, or `None` when it declares no status."""

    matches = _field_matches(item, "status")
    if not matches:
        return None

    label, raw = matches[0]
    if not raw.strip():
        # An empty status is already a fail-closed graph problem; reporting it a
        # second time as a vocabulary defect would just double the noise.
        return None

    value, problem = _status_component(label, raw)
    if value is None:
        return StatusReading(label=label, value=raw.strip(), problem=problem)

    normalized = _normalize_status(value)
    canonical = _LITERAL_STATUSES.get(normalized)
    if canonical is not None:
        return StatusReading(label=label, value=value, canonical=canonical)

    blocked = _BLOCKED_ON_ITEM.match(value.strip())
    if blocked is not None:
        return StatusReading(
            label=label,
            value=value,
            canonical=_STATUS_BLOCKED_TEMPLATE,
            blocker=blocked.group(1),
        )

    for extra in extra_statuses:
        if _normalize_status(extra) == normalized:
            return StatusReading(label=label, value=value, canonical=extra)

    return StatusReading(label=label, value=value, problem=f"unrecognized status {value!r}")


@dataclass(frozen=True)
class RoadmapAnalysis:
    """Derived planning signal: reported facts, advisory warnings, hard problems."""

    metrics: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    problems: tuple[str, ...] = ()


def _percentage(count: int, total: int) -> str:
    return f"{(100.0 * count / total):.1f}%" if total else "0.0%"


def _transitive_dependents(dependencies: dict[str, tuple[str, ...]]) -> dict[str, set[str]]:
    """Map each item to the items that transitively depend on it.

    A reported dependency cycle does not stop the traversal, so the visited set
    is what keeps a cyclic roadmap from looping here.
    """

    dependents: dict[str, set[str]] = {item_id: set() for item_id in dependencies}
    for item_id in dependencies:
        seen: set[str] = set()
        stack = list(dependencies.get(item_id, ()))
        while stack:
            current = stack.pop()
            if current in seen or current not in dependents:
                continue
            seen.add(current)
            if current != item_id:
                dependents[current].add(item_id)
            stack.extend(dependencies.get(current, ()))
    return dependents


def analyze_roadmap(graph: RoadmapGraph, config: RoadmapConfig) -> RoadmapAnalysis:
    """Report the shape of an already-validated roadmap graph.

    This never judges whether an item *should* be blocked and never reorders or
    selects work. It reports the ready surface, the dependency chokepoints, and
    the vocabulary/slice-budget defects that make those numbers unreadable.
    """

    if not graph.items:
        return RoadmapAnalysis()

    path = graph.path
    total = len(graph.items)
    by_id = {item.item_id: item for item in graph.items}

    readings: dict[str, StatusReading] = {}
    vocabulary: list[str] = []
    for item in graph.items:
        reading = read_status(item, extra_statuses=config.extra_statuses)
        if reading is None:
            continue
        readings[item.item_id] = reading
        if reading.problem is not None:
            vocabulary.append(
                f"{path}:{item.line}: structured item {item.item_id} has {reading.problem}; "
                "use a shipped status or extend roadmap.extra_statuses"
            )
        elif reading.blocker == item.item_id:
            vocabulary.append(
                f"{path}:{item.line}: structured item {item.item_id} is blocked by itself"
            )
        elif reading.blocker is not None and reading.blocker not in by_id:
            vocabulary.append(
                f"{path}:{item.line}: structured item {item.item_id} is blocked by unknown item "
                f"{reading.blocker}"
            )

    satisfied = {item_id for item_id, reading in readings.items() if reading.is_satisfying}
    # Closed work stays in the document forever, so measuring the ready surface
    # against every item ever written would decay towards zero on a healthy
    # mature roadmap. Outstanding work is what an agent can actually select from.
    outstanding = {
        item.item_id
        for item in graph.items
        if item.item_id not in satisfied
        and (
            item.item_id not in readings
            or readings[item.item_id].canonical not in _CLOSED_STATUSES
        )
    }
    open_count = len(outstanding)
    ready = [
        item
        for item in graph.items
        if item.item_id in outstanding
        and item.item_id in readings
        and readings[item.item_id].is_workable
        and all(dependency in satisfied for dependency in graph.dependencies.get(item.item_id, ()))
    ]

    if not open_count:
        metrics = [f"ready = 0/0 outstanding; {total} item(s) total, all closed"]
    else:
        metrics = [
            f"ready = {len(ready)}/{open_count} outstanding "
            f"({_percentage(len(ready), open_count)}); {total} item(s) total"
        ]

    dependents = _transitive_dependents(graph.dependencies)
    candidates: dict[str, int] = {}
    for item in graph.items:
        if item.item_id not in outstanding:
            continue
        gated = len(dependents.get(item.item_id, set()) & outstanding)
        if gated and open_count and gated / open_count > config.chokepoint_fraction:
            candidates[item.item_id] = gated

    # Every early link of a long chain formally gates the rest of it. Report only
    # the chokepoints that are not themselves behind another chokepoint, so the
    # output names the item to unblock rather than the chain it sits in.
    chokepoints = [
        (gated, item_id)
        for item_id, gated in candidates.items()
        if not any(
            other != item_id and item_id in dependents.get(other, set())
            for other in candidates
        )
    ]
    for gated, item_id in sorted(chokepoints, key=lambda entry: (-entry[0], entry[1])):
        metrics.append(
            f"chokepoint: {item_id} gates {gated}/{open_count} outstanding "
            f"({_percentage(gated, open_count)})"
        )

    warnings: list[str] = []
    if open_count and (
        len(ready) < config.ready_floor or len(ready) / open_count < config.ready_floor_fraction
    ):
        warnings.append(
            f"ready surface {len(ready)}/{open_count} outstanding "
            f"({_percentage(len(ready), open_count)}) is below the configured floor "
            f"(roadmap.ready_floor={config.ready_floor}, "
            f"roadmap.ready_floor_fraction={config.ready_floor_fraction}); a small ready surface can "
            "be correct while waiting on an external event, so this never fails the check"
        )

    unclassified = total - sum(1 for reading in readings.values() if reading.canonical is not None)
    if unclassified:
        warnings.append(
            f"{unclassified}/{total} item(s) carry a status the ready and chokepoint metrics "
            "cannot classify, so those numbers describe the remainder"
        )

    for item in graph.items:
        reading = readings.get(item.item_id)
        if reading is None or reading.canonical != SLICE_BUDGET_STATUS:
            continue
        budget = _field_matches(item, "slice budget")
        if not budget or not budget[0][1].strip():
            warnings.append(
                f"{path}:{item.line}: structured item {item.item_id} is "
                f"'{SLICE_BUDGET_STATUS}' without **Slice budget:**; declare `k/N` plus the "
                "remaining slices, or split the item into separate IDs"
            )
        elif _SLICE_BUDGET.match(budget[0][1].strip()) is None:
            warnings.append(
                f"{path}:{item.line}: structured item {item.item_id} has malformed "
                f"**Slice budget:** {budget[0][1]!r}; use `k/N`"
            )

    if config.enforce_status_vocabulary:
        return RoadmapAnalysis(
            metrics=tuple(metrics),
            warnings=tuple(warnings),
            problems=tuple(vocabulary),
        )
    return RoadmapAnalysis(metrics=tuple(metrics), warnings=tuple(vocabulary) + tuple(warnings))
