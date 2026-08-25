## Proprietary target experiment workflow

For runtime work against an operator-owned proprietary target, keep acquisition/identity, execution, and evidence packaging explicit:

1. Verify the supplied target and any immutable fixture/data manifest before execution.
2. If the program, emulator, harness, or diagnostic can write into the target tree, create an isolated verified working copy/overlay and leave the supplied source evidence untouched.
3. Run one bounded scenario with predeclared success/failure oracles and termination semantics.
4. Write a detached machine-readable run manifest with an explicit schema/version plus only the bounded logs/captures needed by the question. Include target/fixture hashes, scenario/config identity, harness/tool provenance, material environment facts, termination result, oracle results, and artifact digests. A consumer should reject an unsupported manifest schema rather than guessing how older fields map to current semantics.
5. Sanitize private source paths, usernames, credentials, and unrelated host data before packaging. Never package target executables/assets just because they were convenient inputs to the run.
6. Record the end-to-end operator time the session actually cost, from preparing the environment to handing off the artifact, and carry it into the durable docs. The first successful run on a route is what turns every downstream `Operator cost: unknown (measured by <ID>)` into a real number.

When one session is prepared to satisfy several gated items, verify before the run that source/target/host baselines, scenario/config identity, instrumentation build and run provenance are the same for all of them, and that no item's instrumentation perturbs what another item observes. Name every item the session serves in its run record, and keep their acceptance separate: a shared capture is one run, not one validation.

A target artifact should be self-contained for analysis, not self-contained by redistributing the proprietary target.
