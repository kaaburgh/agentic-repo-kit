## Roadmap Issue projection

When this profile is selected, normalized roadmap items may be projected into GitHub Issues so schedulers can discover and rank work without loading the repository's full planning context first.

The configured roadmap remains the authoritative source for planning state, dependencies, readiness, evidence, acceptance criteria, and sequencing. A projected Issue is a derived scheduling view, never a competing source of truth. If an Issue disagrees with the current roadmap, the roadmap wins and the Issue must be reconciled before its scheduling metadata is trusted.

Each projected roadmap Issue must contain this machine-recognizable contract block, with values appropriate to the current item:

```text
<!-- agentic-roadmap-issue:v1 -->
Roadmap item: <ID>
Canonical source: <roadmap path and item anchor>
Source revision: <commit SHA used for this projection>
Scheduler state: <READY|BLOCKED|BLOCKED_EXTERNAL|ACTIVE|WAITING_REVIEW|DONE>
Blocked by: <projected dependency Issue references or none>
Unblocks: <direct dependent Issue references or none>
```

Keep the Issue lightweight. Link to the canonical roadmap item instead of copying its full rationale, evidence, or acceptance criteria. `Blocked by` projects the item's direct roadmap dependencies. `Unblocks` is only the set of direct dependents that must be re-evaluated when this item changes; it is never an assertion that those Issues become `READY` automatically.

`Scheduler state` and `Source revision` are discovery metadata, not evidence that an item is semantically ready. Before changing repository state for a selected Issue, re-read the current canonical roadmap item, its dependencies and applicable gates. A stale or incorrect projection must be repaired rather than used to justify work.