from __future__ import annotations

import unittest

from agentic_repo_kit.config import RoadmapConfig
from agentic_repo_kit.roadmap import analyze_roadmap, build_roadmap_graph


def warnings_for(text: str) -> tuple[str, ...]:
    analysis = analyze_roadmap(build_roadmap_graph(text), RoadmapConfig())
    return tuple(warning for warning in analysis.warnings if "Slice budget" in warning)


class SliceBudgetTests(unittest.TestCase):
    def test_partially_implemented_item_without_a_budget_is_reported(self) -> None:
        text = '''\
### R1 — Eighth slice, no completion criterion
- **Status:** Partially implemented
- **Depends on:** none
'''
        warnings = warnings_for(text)
        self.assertEqual(1, len(warnings))
        self.assertIn("without **Slice budget:**", warnings[0])

    def test_declared_budget_satisfies_the_rule(self) -> None:
        text = '''\
### R1 — Bounded multi-PR item
- **Status:** Partially implemented
- **Slice budget:** 4/6
- **Depends on:** none
'''
        self.assertEqual((), warnings_for(text))

    def test_malformed_budget_is_reported(self) -> None:
        text = '''\
### R1 — Unbounded budget
- **Status:** Partially implemented
- **Slice budget:** a few more
- **Depends on:** none
'''
        warnings = warnings_for(text)
        self.assertEqual(1, len(warnings))
        self.assertIn("malformed **Slice budget:** 'a few more'", warnings[0])

    def test_compact_status_field_triggers_the_rule(self) -> None:
        text = '''\
### R1 — Compact field
- **Status / priority / execution:** Partially implemented / High / CLOUD
- **Depends on:** none
'''
        self.assertEqual(1, len(warnings_for(text)))

    def test_other_statuses_do_not_trigger_the_rule(self) -> None:
        text = '''\
### R1 — Open
- **Status:** Open
- **Depends on:** none

### R2 — Done
- **Status:** Completed and verified
- **Depends on:** none

### R3 — Blocked
- **Status:** Blocked (R1)
- **Depends on:** R1
'''
        self.assertEqual((), warnings_for(text))

    def test_budget_overrun_is_left_to_the_reviewer(self) -> None:
        # k > N is a review question; the check only establishes that the
        # commitment exists and is readable.
        text = '''\
### R1 — Over budget
- **Status:** Partially implemented
- **Slice budget:** 9/6
- **Depends on:** none
'''
        self.assertEqual((), warnings_for(text))


if __name__ == "__main__":
    unittest.main()
