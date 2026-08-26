from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .adoption import AdoptionPlan, adoption_report, apply_adoption, build_adoption_plan
from .config import load_config
from .errors import AgenticRepoError
from .operations import CONFIG_NAME, bootstrap, check, inspect_repository, roadmap_normalization_packet, upgrade
from .profiles import available_profiles


def _root(value: str) -> Path:
    return Path(value).resolve()


def _config(root: Path, value: str | None) -> Path:
    return Path(value).resolve() if value else root / CONFIG_NAME


def _write_adoption_report(output_value: str, *, root: Path, config_path: Path, plan: AdoptionPlan, report: str) -> Path:
    output = Path(output_value).resolve(strict=False)
    reserved = {config_path.resolve(strict=False)}
    reserved.update((root / item.path).resolve(strict=False) for item in plan.inputs)
    reserved.update((root / item.path).resolve(strict=False) for item in plan.files)
    if output in reserved:
        raise AgenticRepoError(f"adoption plan output collides with an adoption input/managed path: {output}")
    if output.exists() or output.is_symlink():
        raise AgenticRepoError(f"adoption plan output already exists; refusing to overwrite it: {output}")
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(report, encoding="utf-8")
    except OSError as exc:
        raise AgenticRepoError(f"could not write adoption plan output {output}: {exc}") from exc
    return output


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agentic-repo")
    sub = parser.add_subparsers(dest="command", required=True)
    inspect = sub.add_parser("inspect", help="inspect repository signals without changing files")
    inspect.add_argument("root", nargs="?", default=".")
    sub.add_parser("profiles", help="list built-in policy profiles")
    bootstrap_parser = sub.add_parser("bootstrap", help="render the repository agent contract")
    bootstrap_parser.add_argument("root", nargs="?", default=".")
    bootstrap_parser.add_argument("--config")
    bootstrap_parser.add_argument("--force", action="store_true")
    adopt_parser = sub.add_parser("adopt", help="plan or explicitly apply ownership transfer for an existing hand-written contract")
    adopt_parser.add_argument("root", nargs="?", default=".")
    adopt_parser.add_argument("--config")
    adopt_parser.add_argument("--output", help="write the non-destructive adoption plan JSON to a new path")
    adopt_parser.add_argument("--apply", metavar="PLAN_ID", help="apply only the exact reviewed adoption plan identified by this token")
    check_parser = sub.add_parser("check", help="validate generated contract, lock and relative links")
    check_parser.add_argument("root", nargs="?", default=".")
    check_parser.add_argument("--config")
    upgrade_parser = sub.add_parser("upgrade", help="refresh managed generated files for the configured kit")
    upgrade_parser.add_argument("root", nargs="?", default=".")
    upgrade_parser.add_argument("--config")
    normalize = sub.add_parser("normalize-roadmap", help="emit the semantic agent packet used to turn a milestone roadmap into executable work")
    normalize.add_argument("root", nargs="?", default=".")
    normalize.add_argument("--config")
    normalize.add_argument("--output")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "inspect":
            print(json.dumps(inspect_repository(_root(args.root)), indent=2, sort_keys=True))
            return 0
        if args.command == "profiles":
            print("\n".join(available_profiles()))
            return 0
        root = _root(args.root)
        config_path = _config(root, getattr(args, "config", None))
        if args.command == "bootstrap":
            changed = bootstrap(root, config_path, force=args.force)
            print("\n".join(changed) if changed else "repository contract already up to date")
            return 0
        if args.command == "adopt":
            if args.apply:
                if args.output:
                    raise AgenticRepoError("--output is available only in non-destructive adoption plan mode")
                changed = apply_adoption(root, config_path, args.apply)
                print("\n".join(changed) if changed else "adoption plan required no file changes")
                return 0
            plan = build_adoption_plan(root, config_path)
            report = adoption_report(plan)
            if args.output:
                print(_write_adoption_report(args.output, root=root, config_path=config_path, plan=plan, report=report))
            else:
                print(report, end="")
            return 0
        if args.command == "upgrade":
            changed = upgrade(root, config_path)
            print("\n".join(changed) if changed else "repository contract already up to date")
            return 0
        if args.command == "check":
            result = check(root, config_path)
            for metric in result.metrics:
                print(metric)
            for warning in result.warnings:
                print(f"WARNING: {warning}", file=sys.stderr)
            if result.ok:
                print("agentic repository contract is consistent")
                return 0
            for problem in result.problems:
                print(f"ERROR: {problem}", file=sys.stderr)
            return 1
        if args.command == "normalize-roadmap":
            config = load_config(config_path)
            packet = roadmap_normalization_packet(root, config)
            if args.output:
                output = Path(args.output)
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_text(packet, encoding="utf-8")
                print(output)
            else:
                print(packet, end="")
            return 0
    except AgenticRepoError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
