from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from agentic_repo_kit import adoption
from agentic_repo_kit.adoption import apply_adoption, build_adoption_plan
from agentic_repo_kit.errors import AgenticRepoError


CONFIG = '''\
kit_version = 1
profiles = ["core"]

[project]
name = "Adoption race fixture"
kind = "test"
roadmap = "ROADMAP.md"
'''


class SafeAdoptionRaceTests(unittest.TestCase):
    def test_reviewed_roadmap_is_rechecked_immediately_before_writes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config = root / ".agentic-repo.toml"
            roadmap = root / "ROADMAP.md"
            agents = root / "AGENTS.md"
            config.write_text(CONFIG, encoding="utf-8")
            roadmap.write_text("# Roadmap\n", encoding="utf-8")
            agents.write_text("# Legacy agents\n", encoding="utf-8")
            plan = build_adoption_plan(root, config)

            original_render = adoption.render_generated_files
            renders = 0

            def mutate_after_apply_render(config_obj, render_root):
                nonlocal renders
                renders += 1
                result = original_render(config_obj, render_root)
                if renders == 2:
                    roadmap.write_text("# Roadmap\n\nChanged concurrently.\n", encoding="utf-8")
                return result

            with patch("agentic_repo_kit.adoption.render_generated_files", side_effect=mutate_after_apply_render):
                with self.assertRaisesRegex(AgenticRepoError, "roadmap input changed after planning"):
                    apply_adoption(root, config, plan.plan_id)

            self.assertEqual("# Legacy agents\n", agents.read_text(encoding="utf-8"))
            self.assertFalse((root / ".agentic-repo.lock.json").exists())


if __name__ == "__main__":
    unittest.main()
