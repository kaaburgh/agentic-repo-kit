from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from agentic_repo_kit.operations import bootstrap, check
from agentic_repo_kit.roadmap import parse_structured_items, structured_roadmap_problems


CONFIG = '''\
kit_version = 1
profiles = ["core"]

[project]
name = "Roadmap fixture"
kind = "test"
roadmap = "ROADMAP.md"
'''


class RoadmapStructureTests(unittest.TestCase):
    def test_milestone_sketch_without_structured_items_is_ignored(self) -> None:
        text = "# Roadmap\n\n## Milestone 1\n\n- Figure out the architecture.\n"
        self.assertEqual((), parse_structured_items(text))
        self.assertEqual((), structured_roadmap_problems(text))

    def test_valid_dependency_graph_accepts_annotations_and_anchor_links(self) -> None:
        text = '''\
### R1 — Establish baseline
- **Status:** Completed and verified
- **Depends on:** none

### R2 — Analyze target
- **Status:** Open
- **Depends on:** R1 (complete)

### R3 — Validate result
- **Status:** Open
- **Depends on:** [R1](#r1), R2
'''
        self.assertEqual((), structured_roadmap_problems(text))

    def test_duplicate_ids_are_rejected(self) -> None:
        text = '''\
### R1 — First
- **Status:** Open
- **Depends on:** none

### R1 — Duplicate
- **Status:** Open
- **Depends on:** none
'''
        problems = structured_roadmap_problems(text)
        self.assertTrue(any("duplicate roadmap item id 'R1'" in problem for problem in problems))

    def test_required_graph_fields_are_rejected_when_missing(self) -> None:
        text = '''\
### R1 — Missing fields
- **Priority:** High
'''
        problems = structured_roadmap_problems(text)
        self.assertTrue(any("missing **Status:**" in problem for problem in problems))
        self.assertTrue(any("missing **Depends on:**" in problem for problem in problems))

    def test_unknown_self_and_malformed_dependencies_are_rejected(self) -> None:
        text = '''\
### R1 — Broken dependencies
- **Status:** Open
- **Depends on:** R1, R2, not an id with spaces
'''
        problems = structured_roadmap_problems(text)
        self.assertTrue(any("depends on itself" in problem for problem in problems))
        self.assertTrue(any("depends on unknown item R2" in problem for problem in problems))
        self.assertTrue(any("malformed dependency 'not an id with spaces'" in problem for problem in problems))

    def test_dependency_cycle_is_rejected(self) -> None:
        text = '''\
### A — First
- **Status:** Open
- **Depends on:** C

### B — Second
- **Status:** Open
- **Depends on:** A

### C — Third
- **Status:** Open
- **Depends on:** B
'''
        problems = structured_roadmap_problems(text)
        self.assertTrue(any("roadmap dependency cycle:" in problem for problem in problems))

    def test_check_integrates_structural_validation_after_normalization(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config_path = root / ".agentic-repo.toml"
            config_path.write_text(CONFIG, encoding="utf-8")
            (root / "ROADMAP.md").write_text(
                "### R1 — Broken\n- **Status:** Open\n- **Depends on:** MISSING\n",
                encoding="utf-8",
            )
            bootstrap(root, config_path)
            result = check(root, config_path)
            self.assertFalse(result.ok)
            self.assertTrue(any("depends on unknown item MISSING" in problem for problem in result.problems))

    def test_check_keeps_pre_normalization_roadmap_valid(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config_path = root / ".agentic-repo.toml"
            config_path.write_text(CONFIG, encoding="utf-8")
            (root / "ROADMAP.md").write_text(
                "# Roadmap\n\n## Milestone\n\n- high-level idea\n",
                encoding="utf-8",
            )
            bootstrap(root, config_path)
            self.assertTrue(check(root, config_path).ok)


if __name__ == "__main__":
    unittest.main()
