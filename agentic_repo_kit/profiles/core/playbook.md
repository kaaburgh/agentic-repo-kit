## Core execution loop

1. Select one ready roadmap item and verify its dependencies.
2. Inspect current code, docs, tests, CI/build/install paths, and relevant history before changing reality.
3. Separate established facts from assumptions.
4. Choose the smallest change or experiment that can satisfy the item acceptance criteria.
5. Validate what can be validated in the current environment.
6. Reconcile roadmap and durable docs with what was actually learned.
7. Prepare a focused PR with explicit remaining unknowns and deliberately excluded follow-ups.

## Required-capability handoff

If the selected item needs a tool/capability that the current environment lacks:

1. Confirm that the capability is actually required by acceptance/evidence needs; do not escalate merely useful optional cross-checks.
2. Prefer a bounded in-repository implementation when it is a reasonable task-sized substitute with equivalent evidence quality.
3. Try normal install/download/bootstrap/attached-artifact routes available to the environment.
4. If environment constraints block acquisition, continue independent work and package a precise operator handoff: capability/tool, version/platform, why required, attempts made, and exact failures.
5. Do not infer `LOCAL ONLY` or project-level impossibility from one sandbox's acquisition failure.
6. After resolution, preserve the working bootstrap/acquisition path or a useful negative result so the next agent does not repeat the same dead end.
