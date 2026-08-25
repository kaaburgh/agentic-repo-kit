from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from agentic_repo_kit.operations import bootstrap, check


CORE_CONFIG = '''\
kit_version = 1
profiles = ["core"]

[project]
name = "Planning policy fixture"
kind = "test"
roadmap = "ROADMAP.md"
'''

TARGET_CONFIG = '''\
kit_version = 1
profiles = ["core", "proprietary-target"]

[project]
name = "Gated policy fixture"
kind = "test"
roadmap = "ROADMAP.md"
'''


class PlanningWorkabilityPolicyTests(unittest.TestCase):
    def make_repo(self, config: str) -> Path:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        (root / ".agentic-repo.toml").write_text(config, encoding="utf-8")
        (root / "ROADMAP.md").write_text("# Roadmap\n", encoding="utf-8")
        bootstrap(root, root / ".agentic-repo.toml")
        return root

    def test_core_contract_orders_a_vertical_slice_before_formalisation(self) -> None:
        root = self.make_repo(CORE_CONFIG)
        agents = (root / "AGENTS.md").read_text(encoding="utf-8")
        pr = (root / ".github/pull_request_template.md").read_text(encoding="utf-8")

        self.assertIn("Vertical slice before formalisation", agents)
        self.assertIn("one real end-to-end output on the narrowest path", agents)
        self.assertIn("after there is something to conform to", agents)
        self.assertIn("order of operations, not a lower bar", agents)
        self.assertIn("synthetic evidence to be presented as runtime evidence", agents)
        self.assertIn("not a reason to idle", agents)
        self.assertIn("generated rather than accidental", agents)
        self.assertIn("first slice produced one real end-to-end output", pr)
        self.assertTrue(check(root, root / ".agentic-repo.toml").ok)

    def test_core_contract_requires_a_slice_budget_for_multi_pr_items(self) -> None:
        root = self.make_repo(CORE_CONFIG)
        agents = (root / "AGENTS.md").read_text(encoding="utf-8")
        authoring = (root / "docs/roadmap-authoring.md").read_text(encoding="utf-8")
        pr = (root / ".github/pull_request_template.md").read_text(encoding="utf-8")

        self.assertIn("`Slice budget: k/N`", agents)
        self.assertIn("split the item into separate IDs, or re-budget explicitly", agents)
        self.assertIn("Slice budget for multi-PR items", authoring)
        self.assertIn("`Estimated scope: Large` means", authoring)
        self.assertIn("Estimated scope:** Small / Medium / Large", authoring)
        self.assertIn("Slice budget: k/N`; exceeding it splits the item", pr)

    def test_authoring_doc_ships_a_closed_status_vocabulary(self) -> None:
        root = self.make_repo(CORE_CONFIG)
        authoring = (root / "docs/roadmap-authoring.md").read_text(encoding="utf-8")

        self.assertIn("Status is a closed vocabulary, not a free-text field", authoring)
        self.assertIn("`Completed (contract scope)`", authoring)
        self.assertIn("`Blocked (<ID>)`", authoring)
        self.assertIn("extra_statuses", authoring)
        self.assertIn("enforce_status_vocabulary", authoring)
        self.assertIn("rejected fail-closed by kits older than the one that introduced it", authoring)

    def test_authoring_doc_explains_the_derived_planning_metrics(self) -> None:
        root = self.make_repo(CORE_CONFIG)
        authoring = (root / "docs/roadmap-authoring.md").read_text(encoding="utf-8")

        self.assertIn("Derived planning metrics", authoring)
        self.assertIn("well-formed roadmap graph is not the same thing as a workable one", authoring)
        self.assertIn("ready = 2/34 outstanding (5.9%)", authoring)
        self.assertIn("chokepoint:", authoring)
        self.assertIn("They never fail the check", authoring)
        self.assertIn("teach people to work around the check", authoring)
        self.assertIn("does not judge whether an item *should* be blocked", authoring)

    def test_proprietary_target_budgets_operator_attention(self) -> None:
        root = self.make_repo(TARGET_CONFIG)
        agents = (root / "AGENTS.md").read_text(encoding="utf-8")
        playbook = (root / "docs/agent-playbook.md").read_text(encoding="utf-8")
        pr = (root / ".github/pull_request_template.md").read_text(encoding="utf-8")

        self.assertIn("Operator attention is a budgeted resource", agents)
        self.assertIn("Operator cost: <sessions> × <minutes>", agents)
        self.assertIn("Operator cost: unknown (measured by <ID>)", agents)
        self.assertIn("Do not replace it with a plausible-looking estimate", agents)
        self.assertIn("first successful gated run measures the real cost", agents)
        self.assertIn("expected outcome of measurement and a reason to replan", agents)
        self.assertIn("operator-facing derived projection", agents)
        self.assertIn("end-to-end operator time the session actually cost", playbook)
        self.assertIn("Operator cost", pr)
        self.assertTrue(check(root, root / ".agentic-repo.toml").ok)

    def test_proprietary_target_allows_bounded_batching_of_gated_captures(self) -> None:
        root = self.make_repo(TARGET_CONFIG)
        agents = (root / "AGENTS.md").read_text(encoding="utf-8")
        playbook = (root / "docs/agent-playbook.md").read_text(encoding="utf-8")
        pr = (root / ".github/pull_request_template.md").read_text(encoding="utf-8")

        self.assertIn("Batching gated captures", agents)
        self.assertIn("source/target/host baselines, scenario/config identity", agents)
        self.assertIn("Batching does not merge acceptance", agents)
        self.assertIn("forbidden where one item's instrumentation materially changes", agents)
        self.assertIn("run them separately and record why", agents)
        self.assertIn("shared capture is one run, not one validation", playbook)
        self.assertIn("did not merge their acceptance", pr)


if __name__ == "__main__":
    unittest.main()
