from __future__ import annotations

import unittest

from agentic_repo_kit.roadmap import parse_structured_items, structured_roadmap_problems


class RoadmapParserBoundaryTests(unittest.TestCase):
    def test_fieldless_item_reports_required_fields(self) -> None:
        text = '''\
### A1 — Valid item
- **Status:** Open
- **Depends on:** none

### A2 — Empty item
'''
        items = parse_structured_items(text)
        self.assertEqual(("A1", "A2"), tuple(item.item_id for item in items))
        problems = structured_roadmap_problems(text)
        self.assertTrue(any("A2 is missing **Status:**" in problem for problem in problems))
        self.assertTrue(any("A2 is missing **Depends on:**" in problem for problem in problems))

    def test_fenced_schema_example_does_not_create_items(self) -> None:
        text = '''\
### A1 — Real item
- **Status:** Open
- **Depends on:** none

```markdown
### SAMPLE — Example item
- **Status:** Open
- **Depends on:** SAMPLE2
```
'''
        items = parse_structured_items(text)
        self.assertEqual(("A1",), tuple(item.item_id for item in items))
        self.assertEqual((), structured_roadmap_problems(text))


if __name__ == "__main__":
    unittest.main()
