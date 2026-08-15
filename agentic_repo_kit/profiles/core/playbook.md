## Core execution loop

1. Select one ready roadmap item and verify its dependencies; for a process-only change, explicitly establish that no roadmap item applies instead of inventing one.
2. Inspect current code, docs, tests, CI/build/install paths, and only history permitted by the active evidence policy before changing reality. If a blind-research gate excludes unsupported history, do not inspect excluded commits, branches, deleted material, or abandoned work for target-specific investigation.
3. Separate established facts from assumptions.
4. Choose the smallest change or experiment that can satisfy the item acceptance criteria or the explicitly bounded process-only goal.
5. Validate what can be validated in the current environment.
6. Reconcile roadmap and durable docs with what was actually learned.
7. Prepare a focused PR with explicit remaining unknowns and deliberately excluded follow-ups.

## Required-capability handoff

If the selected item or bounded process-only task needs a tool/capability that the current environment lacks:

1. Confirm that the capability is actually required by acceptance/evidence needs; do not escalate merely useful optional cross-checks.
2. Prefer a bounded in-repository implementation when it is a reasonable task-sized substitute with equivalent evidence quality.
3. Try normal install/download/bootstrap/attached-artifact routes available to the environment.
4. If environment constraints block acquisition, continue independent work and package a precise operator handoff: capability/tool, version/platform, why required, attempts made, and exact failures.
5. Do not infer `LOCAL ONLY` or project-level impossibility from one sandbox's acquisition failure.
6. After resolution, preserve the working bootstrap/acquisition path or a useful negative result so the next agent does not repeat the same dead end.

## Evidence-producing CI and regression triggers

A regression workflow is part of the evidence chain, not merely a convenient command runner. If a job validates a parser, generated dataset, acquisition path, target-specific analyzer, patch locator, or other durable evidence, its trigger/filter set must cover every material repository input that can change that evidence: the entry-point script plus shared parsers/libraries, schemas, manifests, acquisition/configuration data, and other producer dependencies.

Do not let a path-filter optimization create a false green by skipping the dedicated regression when one of its shared inputs changes. When the dependency surface is difficult to express safely, prefer a broader trigger over an incomplete narrow filter.

Where reproducible inputs are available, run the repository's real entry point from a clean checkout instead of validating a hand-reproduced equivalent implementation. Synthetic tests remain valuable for edge cases, but they do not replace a clean-checkout end-to-end regression when the acceptance claim depends on the real producer/target/input chain.

When a producer's serialized output semantics change, version or invalidate the affected derived evidence and ensure the regression exercises the new consumer/producer compatibility boundary rather than silently reusing stale artifacts.
