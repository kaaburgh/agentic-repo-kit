from __future__ import annotations

from hashlib import sha256
from importlib.resources import files
import json
from pathlib import Path
import re

from . import __version__
from .errors import AgenticRepoError


DISTRIBUTION_REPOSITORY = "kaaburgh/agentic-repo-kit"
DISTRIBUTION_METADATA = "distribution.json"
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def artifact_name(version: str = __version__) -> str:
    return f"agentic-repo-kit-{version}.pyz"


def release_tag(version: str = __version__) -> str:
    return f"v{version}"


def _running_zipapp() -> Path | None:
    loader = globals().get("__loader__")
    archive = getattr(loader, "archive", None)
    if not archive:
        return None
    path = Path(str(archive)).resolve()
    return path if path.is_file() else None


def _validate_identity(raw: object) -> dict[str, str]:
    if not isinstance(raw, dict):
        raise AgenticRepoError("invalid executable distribution metadata")
    expected = {
        "repository": DISTRIBUTION_REPOSITORY,
        "release": release_tag(),
        "artifact": artifact_name(),
        "tool_version": __version__,
    }
    for key, value in expected.items():
        if raw.get(key) != value:
            raise AgenticRepoError(
                f"executable distribution metadata mismatch for {key}: "
                f"expected {value!r}, got {raw.get(key)!r}"
            )
    digest = raw.get("sha256")
    if not isinstance(digest, str) or not _SHA256_RE.fullmatch(digest):
        raise AgenticRepoError("invalid executable distribution sha256")
    return {**expected, "sha256": digest}


def distribution_identity() -> dict[str, str]:
    """Return the pinned executable distribution identity for the running kit.

    Source/wheel installs read committed metadata. The deterministic zipapp omits
    that metadata file and instead hashes its own archive, avoiding a digest
    self-reference while producing the same lock identity.
    """

    archive = _running_zipapp()
    if archive is not None:
        return {
            "repository": DISTRIBUTION_REPOSITORY,
            "release": release_tag(),
            "artifact": artifact_name(),
            "tool_version": __version__,
            "sha256": sha256(archive.read_bytes()).hexdigest(),
        }

    try:
        raw = json.loads(
            files("agentic_repo_kit")
            .joinpath(DISTRIBUTION_METADATA)
            .read_text(encoding="utf-8")
        )
    except (FileNotFoundError, json.JSONDecodeError, OSError) as exc:
        raise AgenticRepoError("cannot read executable distribution metadata") from exc
    return _validate_identity(raw)
