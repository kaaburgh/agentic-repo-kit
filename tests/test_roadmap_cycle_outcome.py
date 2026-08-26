from __future__ import annotations

import unittest

from agentic_repo_kit.config import RoadmapConfig
from agentic_repo_kit.cycle_outcome import cycle_outcome_warnings
from agentic_repo_kit.roadmap import build_roadmap_graph


def warnings_for(text: str) -> tuple[str, ...]:
    return cycle_outcome_warnings(build_roadmap_graph(text), RoadmapConfig())


class CycleOutcomeTests(unittest.TestCase):
    def test_investigation_item_without_outcome_warns(self) -> None:
        text = '''\
### R1 — Open question across cycles
- **Status:** Investigation first
- **Depends on:** none
'''
        warnings = warnings_for(text)
        self.assertEqual(1, len(warnings))
        self.assertIn("without **Cycle outcome:**", warnings[0])

    def test_partially_implemented_item_without_outcome_warns(self) -> None:
        text = '''\
### R1 — Multi-PR implementation
- **Status:** Partially implemented
- **Depends on:** none
'''
        self.assertEqual(1, len(warnings_for(text)))

    def test_other_statuses_do_not_require_the_field(self) -> None:
        text = '''\
### R1 — Fresh work
- **Status:** Open
- **Depends on:** none

### R2 — Validation remains
- **Status:** Implemented, validation incomplete
- **Depends on:** none

### R3 — Done
- **Status:** Completed and verified
- **Depends on:** none
'''
        self.assertEqual((), warnings_for(text))

    def test_simple_outcomes_are_parseable(self) -> None:
        for outcome in ("evidence", "durable negative", "operator handoff"):
            with self.subTest(outcome=outcome):
                text = f'''\
### R1 — Classified cycle
- **Status:** Investigation first
- **Cycle outcome:** {outcome}
- **Depends on:** none
'''
                self.assertEqual((), warnings_for(text))

    def test_tooling_only_positive_streak_and_unknown_are_parseable(self) -> None:
        for streak in ("1", "17", "unknown"):
            with self.subTest(streak=streak):
                text = f'''\
### R1 — Tooling sequence
- **Status:** Investigation first
- **Cycle outcome:** tooling only ({streak}) — run the already-built producer
- **Depends on:** none
'''
                self.assertEqual((), warnings_for(text))

    def test_zero_count_is_distinct_from_unknown_and_warns(self) -> None:
        text = '''\
### R1 — Invalid zero
- **Status:** Investigation first
- **Cycle outcome:** tooling only (0) — run the producer
- **Depends on:** none
'''
        warnings = warnings_for(text)
        self.assertEqual(1, len(warnings))
        self.assertIn("malformed **Cycle outcome:**", warnings[0])

    def test_tooling_only_requires_a_remaining_step(self) -> None:
        text = '''\
### R1 — Missing next step
- **Status:** Investigation first
- **Cycle outcome:** tooling only (3) —
- **Depends on:** none
'''
        self.assertEqual(1, len(warnings_for(text)))

    def test_cycle_outcome_must_be_standalone(self) -> None:
        text = '''\
### R1 — Compact field cannot be parsed safely
- **Status:** Investigation first
- **Cycle outcome / priority:** evidence / High
- **Depends on:** none
'''
        warnings = warnings_for(text)
        self.assertEqual(1, len(warnings))
        self.assertIn("standalone **Cycle outcome:**", warnings[0])


if __name__ == "__main__":
    unittest.main()
