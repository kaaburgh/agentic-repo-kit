## Proprietary target material

Do not commit proprietary executables/assets, private dumps, secrets, credentials, or unnecessarily large captures. Commit only the minimal derived metadata and tooling needed to reproduce and review the work.

Treat operator-supplied proprietary target trees as immutable evidence inputs. Verify the exact target/fixture identity before use and, when the target or harness can write to its mounted tree, execute against a verified copy, isolated work directory, overlay, or equivalent mechanism rather than mutating the source evidence in place. Reject ambiguous target/fixture selection instead of choosing one silently.

When a target machine is required, prepare the smallest reproducible one-shot experiment. Prefer a script/tool that verifies the target/fixture identity, executes one bounded scenario, and emits a self-contained artifact containing only safe metadata, hashes/version identifiers, configuration, bounded logs, and the requested captures/dumps.

The detached machine-readable run record should have an explicit schema/version and preserve enough provenance to replay and audit the evidence without redistributing the target: target/fixture identities, scenario/config identity, harness/tool versions or hashes, material environment facts, termination result, semantic oracle results, and artifact names/digests. Sanitize private host paths, user identifiers, credentials, and unrelated environment data. Do not embed proprietary payload bytes in the run record merely for convenience.
