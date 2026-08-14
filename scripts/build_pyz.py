from __future__ import annotations

import argparse
from hashlib import sha256
from pathlib import Path
import stat
import zipfile


FIXED_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
MAIN = b"from agentic_repo_kit.cli import main\nraise SystemExit(main())\n"
EXCLUDED_NAMES = {"distribution.json"}


def _write_entry(zf: zipfile.ZipFile, name: str, data: bytes) -> None:
    info = zipfile.ZipInfo(name, FIXED_TIMESTAMP)
    info.create_system = 3
    info.external_attr = (stat.S_IFREG | 0o644) << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    zf.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def build_pyz(root: Path, output: Path) -> str:
    root = root.resolve()
    package = root / "agentic_repo_kit"
    if not package.is_dir():
        raise SystemExit(f"package directory not found: {package}")

    entries: list[tuple[str, bytes]] = [("__main__.py", MAIN)]
    for path in sorted(package.rglob("*")):
        if not path.is_file():
            continue
        if path.name in EXCLUDED_NAMES or path.suffix == ".pyc" or "__pycache__" in path.parts:
            continue
        entries.append((path.relative_to(root).as_posix(), path.read_bytes()))

    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w") as zf:
        for name, data in entries:
            _write_entry(zf, name, data)

    return sha256(output.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Build deterministic agentic-repo-kit zipapp")
    parser.add_argument("--root", default=".")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    digest = build_pyz(Path(args.root), Path(args.output))
    print(digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
