from __future__ import annotations

import unittest

from agentic_repo_kit.roadmap import parse_structured_items, structured_roadmap_problems


class RoadmapDogfoodVariantTests(unittest.TestCase):
    def test_level_two_and_level_three_items_are_supported(self) -> None:
        text = '''\
# Track A

## A1 — First item
- **Status:** Completed and verified
- **Depends on:** None

### Outcome
- Nested prose remains inside the item.

## A2 — Follow-up
- **Status:** Open
- **Depends on:** `A1` (complete)

# Milestone B

### B1 — Compact status item
- **Status / priority / execution:** Open / Critical / CLOUD RESEARCH
- **Depends on:** [A1](#a1), **A2**
'''
        items = parse_structured_items(text)
        self.assertEqual(("A1", "A2", "B1"), tuple(item.item_id for item in items))
        self.assertEqual((2, 2, 3), tuple(item.heading_level for item in items))
        self.assertEqual((), structured_roadmap_problems(text))

    def test_fieldless_section_heading_is_not_an_item(self) -> None:
        text = '''\
## M0 — Milestone section

> Section outcome only.

### A1 — Real item
- **Status:** Open
- **Depends on:** none
'''
        items = parse_structured_items(text)
        self.assertEqual(("A1",), tuple(item.item_id for item in items))
        self.assertEqual((), structured_roadmap_problems(text))

    def test_same_or_higher_heading_closes_current_item(self) -> None:
        text = '''\
### R1 — First
- **Status:** Open
- **Depends on:** none

## Notes
- **Depends on:** OTHER

### R2 — Second
- **Status:** Open
- **Depends on:** R1
'''
        items = parse_structured_items(text)
        self.assertEqual(("R1", "R2"), tuple(item.item_id for item in items))
        self.assertEqual("none", items[0].fields["depends on"])
        self.assertEqual((), structured_roadmap_problems(text))

    def test_duplicate_field_is_reported(self) -> None:
        text = '''\
### R1 — Item
- **Status:** Open
- **Status:** Blocked
- **Depends on:** none
'''
        problems = structured_roadmap_problems(text)
        self.assertTrue(any("repeats field **status:**" in problem for problem in problems))


if __name__ == "__main__":
    unittest.main()
