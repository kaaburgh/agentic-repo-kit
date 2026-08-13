from __future__ import annotations

from importlib.resources import files

from .errors import AgenticRepoError


FRAGMENTS = ("agents.md", "playbook.md", "pr.md")


def available_profiles() -> tuple[str, ...]:
    root = files("agentic_repo_kit").joinpath("profiles")
    return tuple(sorted(item.name for item in root.iterdir() if item.is_dir()))


def load_fragment(profile: str, fragment: str) -> str:
    if fragment not in FRAGMENTS:
        raise ValueError(fragment)
    root = files("agentic_repo_kit").joinpath("profiles", profile)
    if not root.is_dir():
        known = ", ".join(available_profiles())
        raise AgenticRepoError(f"unknown profile '{profile}' (available: {known})")
    path = root.joinpath(fragment)
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8").strip()
