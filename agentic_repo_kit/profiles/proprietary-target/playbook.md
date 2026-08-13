## Proprietary target experiment workflow

For runtime work against an operator-owned proprietary target, keep acquisition/identity, execution, and evidence packaging explicit:

1. Verify the supplied target and any immutable fixture/data manifest before execution.
2. If the program, emulator, harness, or diagnostic can write into the target tree, create an isolated verified working copy/overlay and leave the supplied source evidence untouched.
3. Run one bounded scenario with predeclared success/failure oracles and termination semantics.
4. Write a detached run manifest plus only the bounded logs/captures needed by the question. Include target/fixture hashes, scenario/config identity, harness/tool provenance, material environment facts, termination result, oracle results, and artifact digests.
5. Sanitize private source paths, usernames, credentials, and unrelated host data before packaging. Never package target executables/assets just because they were convenient inputs to the run.

A target artifact should be self-contained for analysis, not self-contained by redistributing the proprietary target.
