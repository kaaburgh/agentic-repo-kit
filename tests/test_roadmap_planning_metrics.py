from __future__ import annotations

import contextlib
import io
from pathlib import Path
import tempfile
import unittest

from agentic_repo_kit.cli import main
from agentic_repo_kit.config import RoadmapConfig
from agentic_repo_kit.operations import bootstrap, check
from agentic_repo_kit.roadmap import analyze_roadmap, build_roadmap_graph


CONFIG = '''\
kit_version = 1
profiles = ["core"]

[project]
name = "Planning metrics fixture"
kind = "test"
roadmap = "ROADMAP.md"
'''


def gated_roadmap() -> str:
    """A well-formed graph that is nonetheless unworkable.

    Reproduces the reviewed shape: one never-validated item gating most of the
    roadmap, two ready items, and a long chain of blocked slices behind it.
    """

    items = [
        "### ENV1 — Establish the runtime route\n"
        "- **Status:** Blocked on target evidence\n"
        "- **Depends on:** none\n"
    ]
    previous = "ENV1"
    for index in range(1, 23):
        items.append(
            f"### G{index} — Gated slice {index}\n"
            f"- **Status:** Blocked (ENV1)\n"
            f"- **Depends on:** {previous}\n"
        )
        previous = f"G{index}"
    items.append(
        "### C1 — Contract slice\n"
        "- **Status:** Partially implemented\n"
        "- **Slice budget:** 4/6\n"
        "- **Depends on:** none\n"
    )
    items.append("### C2 — Second lane\n- **Status:** Open\n- **Depends on:** none\n")
    for index in range(1, 10):
        items.append(
            f"### X{index} — Side item {index}\n"
            f"- **Status / priority / execution:** Blocked (ENV1) / High / GATED\n"
            f"- **Depends on:** ENV1\n"
        )
    return "\n".join(items)


def analyze(text: str, config: RoadmapConfig | None = None):
    return analyze_roadmap(build_roadmap_graph(text), config or RoadmapConfig())


class PlanningMetricsTests(unittest.TestCase):
    def test_ready_surface_and_chokepoint_are_reported(self) -> None:
        analysis = analyze(gated_roadmap())
        self.assertEqual("ready = 2/34 outstanding (5.9%); 34 item(s) total", analysis.metrics[0])
        self.assertIn("chokepoint: ENV1 gates 31/34 outstanding (91.2%)", analysis.metrics)

    def test_only_maximal_chokepoints_are_reported(self) -> None:
        # Every early link of the chain formally gates the rest of it; naming
        # them all would bury the one item that actually has to be unblocked.
        chokepoints = [metric for metric in analyze(gated_roadmap()).metrics if "chokepoint" in metric]
        self.assertEqual(1, len(chokepoints))

    def test_ready_requires_workable_status_and_satisfied_dependencies(self) -> None:
        text = '''\
### R1 — Done
- **Status:** Completed and verified
- **Depends on:** none

### R2 — Ready behind a completed dependency
- **Status:** Open
- **Depends on:** R1

### R3 — Not ready behind unfinished work
- **Status:** Open
- **Depends on:** R2

### R4 — Not workable
- **Status:** Blocked on target evidence
- **Depends on:** none
'''
        self.assertEqual("ready = 1/3 outstanding (33.3%); 4 item(s) total", analyze(text).metrics[0])

    def test_closed_work_leaves_the_denominator(self) -> None:
        # A mature roadmap accumulates closed items forever; measuring against
        # every item ever written would decay towards zero regardless of health.
        text = "".join(
            f"### D{index} — Done {index}\n- **Status:** Completed and verified\n- **Depends on:** none\n\n"
            for index in range(1, 20)
        ) + "### R1 — Current work\n- **Status:** Open\n- **Depends on:** none\n"
        analysis = analyze(text)
        self.assertEqual("ready = 1/1 outstanding (100.0%); 20 item(s) total", analysis.metrics[0])
        self.assertFalse(any("ready surface" in warning for warning in analysis.warnings))

    def test_fully_closed_roadmap_reports_no_floor_warning(self) -> None:
        text = "### D1 — Done\n- **Status:** Completed and verified\n- **Depends on:** none\n"
        analysis = analyze(text)
        self.assertEqual("ready = 0/0 outstanding; 1 item(s) total, all closed", analysis.metrics[0])
        self.assertFalse(any("ready surface" in warning for warning in analysis.warnings))

    def test_thresholds_are_configurable(self) -> None:
        text = gated_roadmap()
        relaxed = analyze(text, RoadmapConfig(ready_floor=0, ready_floor_fraction=0.0))
        self.assertFalse(any("ready surface" in warning for warning in relaxed.warnings))

        strict = analyze(text, RoadmapConfig(chokepoint_fraction=0.95))
        self.assertFalse(any("chokepoint" in metric for metric in strict.metrics))

    def test_unclassified_statuses_are_declared_alongside_the_metrics(self) -> None:
        text = '''\
### R1 — Invented status
- **Status:** Mostly fine
- **Depends on:** none

### R2 — Open
- **Status:** Open
- **Depends on:** none
'''
        warnings = analyze(text).warnings
        self.assertTrue(any("1/2 item(s) carry a status" in warning for warning in warnings))

    def test_milestone_sketch_produces_no_metrics(self) -> None:
        analysis = analyze("# Roadmap\n\n## Milestone\n\n- high-level idea\n")
        self.assertEqual((), analysis.metrics)
        self.assertEqual((), analysis.warnings)

    def test_metrics_never_turn_a_passing_check_into_a_failing_one(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config_path = root / ".agentic-repo.toml"
            config_path.write_text(CONFIG, encoding="utf-8")
            (root / "ROADMAP.md").write_text(gated_roadmap(), encoding="utf-8")
            bootstrap(root, config_path)

            result = check(root, config_path)
            self.assertTrue(result.ok)
            self.assertEqual((), result.problems)
            self.assertTrue(any("chokepoint: ENV1" in metric for metric in result.metrics))
            self.assertTrue(any("ready surface" in warning for warning in result.warnings))

    def test_cli_reports_metrics_on_stdout_and_warnings_on_stderr(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config_path = root / ".agentic-repo.toml"
            config_path.write_text(CONFIG, encoding="utf-8")
            (root / "ROADMAP.md").write_text(gated_roadmap(), encoding="utf-8")
            bootstrap(root, config_path)

            stdout, stderr = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                code = main(["check", str(root)])

            self.assertEqual(0, code)
            self.assertIn("ready = 2/34 outstanding (5.9%)", stdout.getvalue())
            self.assertIn("chokepoint: ENV1 gates", stdout.getvalue())
            self.assertIn("consistent", stdout.getvalue())
            self.assertIn("WARNING: ready surface", stderr.getvalue())
            self.assertNotIn("ERROR", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
