## Roadmap Issue scheduling projection

Use projected roadmap Issues for cheap discovery and ranking only. Do not load every repository deeply just to find work.

When selecting work through the projection:

1. scan projected Issue metadata and active PR state cheaply;
2. choose the best actionable Issue globally according to the caller's scheduling policy;
3. only then load that repository's current contract and canonical roadmap item;
4. verify the selected item's current dependencies, gates, scope, and acceptance criteria against the roadmap before writing;
5. if the Issue projection is stale or wrong, reconcile it before relying on its scheduler state.

When a roadmap-scoped PR changes the selected item's planning state, reconcile that Issue's projection. If the change completes or otherwise changes a dependency, re-evaluate every Issue named by `Unblocks` against all of its own `Blocked by` dependencies and applicable roadmap gates. Never mark a dependent `READY` merely because one predecessor completed.

Projection reconciliation must be idempotent. A later agent must be able to finish or repeat reconciliation safely if the repository change or PR merge succeeded but one or more GitHub Issue updates did not. Closing a projected Issue is appropriate only when the canonical roadmap item has reached a terminal state; partial progress keeps the Issue open with reconciled scheduler metadata.