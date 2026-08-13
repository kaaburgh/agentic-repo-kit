Treat the existing roadmap as source material, not as an executable backlog yet.

1. Read repository instructions, README, current roadmap, build/CI/install scripts, durable technical docs, issues/PRs that materially constrain the current milestone, and current source structure.
2. Preserve product intent and milestone outcomes unless current evidence disproves them.
3. Convert milestone-level bullets into bounded investigation or implementation items with stable IDs, explicit dependencies, acceptance criteria, durable artifact destinations, expected information gain for investigations, and execution-environment classification where relevant.
4. Do not encode unknown implementation details as facts. Create an investigation item when state representation, call path, compatibility boundary, feasibility, or root cause is not established.
5. Prefer dependency-unlocking experiments with high information gain. Separate “find the seam” from “ship the patch/fix”.
6. Keep one item small enough for one focused PR. Name tempting adjacent work as later items rather than widening scope.
7. Preserve negative results and prior decisions that prevent repeated dead ends.
8. Ensure the roadmap tells an agent which ready item may be selected next without chat history.
9. Reconcile README or supporting docs only where the normalized roadmap changes project-level claims.
10. Validate Markdown links and any repository-specific documentation checks after editing.

The normalization pass may change the roadmap structure substantially, but it must not claim implementation or target-runtime validation that did not occur during the pass.
