## Roadmap Issue projection

- Link the projected GitHub Issue and the canonical roadmap item when this PR is roadmap-scoped.
- State whether the PR completes the roadmap item or leaves it non-terminal; do not use automatic Issue closure for partial progress.
- Reconcile the selected Issue's scheduler metadata when roadmap state changes, and re-evaluate the direct dependents named by `Unblocks` when dependency state changes.
- Treat any Issue projection as derived metadata: the current roadmap and exact PR head remain authoritative for planning and review claims.