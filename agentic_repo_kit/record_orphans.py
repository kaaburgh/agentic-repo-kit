from __future__ import annotations

from pathlib import Path
import re
from urllib.parse import unquote

from .errors import AgenticRepoError
from .paths import confined_repo_path
from .roadmap import RoadmapGraph, RoadmapItem


_HEADING = re.compile(r"^(#{1,6})\s+")
_FENCE = re.compile(r"^\s*(```|~~~)")
_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def _item_section(text: str, item: RoadmapItem) -> str:
    lines = text.splitlines()
    start = max(item.line - 1, 0)
    end = len(lines)
    in_fence = False
    fence_marker = ""

    for index in range(start + 1, len(lines)):
        line = lines[index]
        fence = _FENCE.match(line)
        if fence:
            marker = fence.group(1)
            if not in_fence:
                in_fence = True
                fence_marker = marker
            elif marker == fence_marker:
                in_fence = False
                fence_marker = ""
            continue
        if in_fence:
            continue
        heading = _HEADING.match(line)
        if heading and len(heading.group(1)) <= item.heading_level:
            end = index
            break
    return "\n".join(lines[start:end])


def _relative_links(section: str, *, roadmap_parent: Path, root: Path) -> set[Path]:
    root_resolved = root.resolve()
    result: set[Path] = set()
    in_fence = False
    fence_marker = ""
    for line in section.splitlines():
        fence = _FENCE.match(line)
        if fence:
            marker = fence.group(1)
            if not in_fence:
                in_fence = True
                fence_marker = marker
            elif marker == fence_marker:
                in_fence = False
                fence_marker = ""
            continue
        if in_fence:
            continue
        for target in _LINK.findall(line):
            target = target.strip().split("#", 1)[0]
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            resolved = (roadmap_parent / unquote(target)).resolve(strict=False)
            try:
                resolved.relative_to(root_resolved)
            except ValueError:
                continue
            result.add(resolved)
    return result


def _configured_records(root: Path, directories: tuple[str, ...]) -> tuple[set[Path], list[str]]:
    records: set[Path] = set()
    warnings: list[str] = []
    for relative in directories:
        try:
            directory = confined_repo_path(root, relative, label="roadmap.record_directories entry")
        except AgenticRepoError as exc:
            warnings.append(str(exc))
            continue
        if not directory.exists():
            warnings.append(f"configured roadmap record directory does not exist: {relative}")
            continue
        if not directory.is_dir():
            warnings.append(f"configured roadmap record directory is not a directory: {relative}")
            continue
        for path in directory.rglob("*"):
            if path.is_symlink() or not path.is_file():
                continue
            records.add(path.resolve())
    return records, warnings


def record_orphan_warnings(
    root: Path,
    roadmap: Path,
    roadmap_text: str,
    graph: RoadmapGraph,
    directories: tuple[str, ...],
) -> tuple[str, ...]:
    """Report configured durable records that no roadmap item section links to.

    This is a workability signal, not a well-formedness failure. A record can be
    legitimately cross-cutting or historical, so callers expose these strings
    through the warning channel only.
    """

    if not directories:
        return ()

    records, warnings = _configured_records(root, directories)
    if not records:
        return tuple(warnings)

    linked: set[Path] = set()
    for item in graph.items:
        linked.update(
            _relative_links(
                _item_section(roadmap_text, item),
                roadmap_parent=roadmap.parent,
                root=root,
            )
        )

    unreferenced = sorted(records - linked, key=lambda path: path.as_posix())
    if unreferenced:
        root_resolved = root.resolve()
        relative = [path.relative_to(root_resolved).as_posix() for path in unreferenced]
        warnings.append(
            f"{graph.path}: {len(relative)} configured durable record(s) are not linked from any "
            f"roadmap item section: {', '.join(relative)}"
        )
    return tuple(warnings)
