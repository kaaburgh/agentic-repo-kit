from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from agentic_repo_kit.config import RoadmapConfig
from agentic_repo_kit.operations import bootstrap, check
from agentic_repo_kit.roadmap import (
    CANONICAL_STATUSES,
    analyze_roadmap,
    build_roadmap_graph,
    parse_structured_items,
    read_status,
)


CONFIG = '''\
kit_version = 1
profiles = ["core"]

[project]
name = "Status vocabulary fixture"
kind = "test"
roadmap = "ROADMAP.md"
'''


def analyze(text: str, config: RoadmapConfig | None = None):
    return analyze_roadmap(build_roadmap_graph(text), config or RoadmapConfig())


class StatusVocabularyTests(unittest.TestCase):
    def test_shipped_vocabulary_covers_contract_scope_and_named_blockers(self) -> None:
        self.assertIn("Completed (contract scope)", CANONICAL_STATUSES)
        self.assertIn("Blocked (<ID>)", CANONICAL_STATUSES)

    def test_canonical_statuses_produce_no_vocabulary_warning(self) -> None:
        text = '''\
### R1 — Contract closed without target evidence
- **Status:** Completed (contract scope)
- **Depends on:** none

### R2 — Named blocker
- **Status:** Blocked (R1)
- **Depends on:** R1
'''
        analysis = analyze(text)
        self.assertEqual((), analysis.problems)
        self.assertEqual(
            (),
            tuple(warning for warning in analysis.warnings if "status" in warning),
        )

    def test_compact_status_field_is_read_positionally(self) -> None:
        text = '''\
### R1 — Compact field
- **Status / priority / execution:** Open / Critical / CLOUD RESEARCH
- **Depends on:** none
'''
        reading = read_status(parse_structured_items(text)[0])
        self.assertEqual("Open", reading.canonical)
        self.assertIsNone(reading.problem)
        self.assertFalse(
            any("unrecognized status" in warning for warning in analyze(text).warnings)
        )

    def test_compact_status_field_with_mismatched_components_is_reported(self) -> None:
        text = '''\
### R1 — Compact field with a short value
- **Status / priority / execution:** Open
- **Depends on:** none
'''
        warnings = analyze(text).warnings
        self.assertTrue(any("cannot be read positionally" in warning for warning in warnings))

    def test_unrecognized_status_warns_without_failing(self) -> None:
        text = '''\
### R1 — Invented status
- **Status:** Mostly fine
- **Depends on:** none
'''
        analysis = analyze(text)
        self.assertEqual((), analysis.problems)
        self.assertTrue(
            any("unrecognized status 'Mostly fine'" in warning for warning in analysis.warnings)
        )

    def test_named_blocker_must_resolve_to_a_known_item(self) -> None:
        text = '''\
### R1 — Blocked by a typo
- **Status:** Blocked (R404)
- **Depends on:** none
'''
        warnings = analyze(text).warnings
        self.assertTrue(any("blocked by unknown item R404" in warning for warning in warnings))

    def test_item_blocked_by_itself_is_reported(self) -> None:
        text = '''\
### R1 — Blocked by itself
- **Status:** Blocked (R1)
- **Depends on:** none
'''
        warnings = analyze(text).warnings
        self.assertTrue(any("R1 is blocked by itself" in warning for warning in warnings))

    def test_empty_status_is_not_reported_twice(self) -> None:
        text = '''\
### R1 — Empty status
- **Status:**
- **Depends on:** none
'''
        graph = build_roadmap_graph(text)
        self.assertTrue(any("missing **Status:**" in problem for problem in graph.problems))
        self.assertFalse(
            any("unrecognized status" in warning for warning in analyze(text).warnings)
        )

    def test_project_extension_is_accepted_but_carries_no_semantics(self) -> None:
        text = '''\
### R1 — Project specific status
- **Status:** Awaiting legal review
- **Depends on:** none
'''
        config = RoadmapConfig(extra_statuses=("Awaiting legal review",))
        analysis = analyze(text, config)
        self.assertFalse(any("unrecognized status" in warning for warning in analysis.warnings))
        # An extension is valid but is not workable, so it never counts as ready.
        self.assertIn("ready = 0/1 outstanding", analysis.metrics[0])

    def test_enforcement_promotes_vocabulary_warnings_to_problems(self) -> None:
        text = '''\
### R1 — Invented status
- **Status:** Mostly fine
- **Depends on:** none
'''
        analysis = analyze(text, RoadmapConfig(enforce_status_vocabulary=True))
        self.assertTrue(any("unrecognized status" in problem for problem in analysis.problems))
        self.assertFalse(any("unrecognized status" in warning for warning in analysis.warnings))

    def test_check_warns_by_default_and_fails_only_when_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config_path = root / ".agentic-repo.toml"
            config_path.write_text(CONFIG, encoding="utf-8")
            (root / "ROADMAP.md").write_text(
                "### R1 — Invented status\n- **Status:** Mostly fine\n- **Depends on:** none\n",
                encoding="utf-8",
            )
            bootstrap(root, config_path)

            default = check(root, config_path)
            self.assertTrue(default.ok)
            self.assertTrue(any("unrecognized status" in w for w in default.warnings))

            config_path.write_text(
                CONFIG + "\n[roadmap]\nenforce_status_vocabulary = true\n", encoding="utf-8"
            )
            enforced = check(root, config_path)
            self.assertFalse(enforced.ok)
            self.assertTrue(any("unrecognized status" in p for p in enforced.problems))


if __name__ == "__main__":
    unittest.main()
