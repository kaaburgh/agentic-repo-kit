## Proprietary target material

Do not commit proprietary executables/assets, private dumps, secrets, credentials, or unnecessarily large captures. Commit only the minimal derived metadata and tooling needed to reproduce and review the work.

Treat operator-supplied proprietary target trees as immutable evidence inputs. Verify the exact target/fixture identity before use and, when the target or harness can write to its mounted tree, execute against a verified copy, isolated work directory, overlay, or equivalent mechanism rather than mutating the source evidence in place. Reject ambiguous target/fixture selection instead of choosing one silently.

When a target machine is required, prepare the smallest reproducible one-shot experiment. Prefer a script/tool that verifies the target/fixture identity, executes one bounded scenario, and emits a self-contained artifact containing only safe metadata, hashes/version identifiers, configuration, bounded logs, and the requested captures/dumps.

The detached machine-readable run record should have an explicit schema/version and preserve enough provenance to replay and audit the evidence without redistributing the target: target/fixture identities, scenario/config identity, harness/tool versions or hashes, material environment facts, termination result, semantic oracle results, and artifact names/digests. Sanitize private host paths, user identifiers, credentials, and unrelated environment data. Do not embed proprietary payload bytes in the run record merely for convenience.

## Operator attention is a budgeted resource

Gated work spends a person's time. Compute is elastic; the operator who owns the proprietary target is not. Machinery for classifying, preparing and packaging gated work does not by itself ask how much of that person's time the plan requires in total, and a plan that never asks can accumulate to tens of hours of manual work that appears nowhere in it.

Every gated item states an operator cost:

- `Operator cost: <sessions> × <minutes>` — a measured or explicitly derived estimate, or
- `Operator cost: unknown (measured by <ID>)` — naming the item that will establish it.

`unknown` is a permitted and durable value. Do not replace it with a plausible-looking estimate: an invented operator cost is an invented number under the same rule that forbids inventing commands, targets, performance numbers, supported versions, and architecture details. Until a real measurement exists, every other gated estimate is a guess and the plan should say so rather than let confident-looking numbers accumulate.

The first successful gated run measures the real cost. The feasibility item that establishes the route records actual end-to-end operator time — preparing the environment, launching, waiting, packaging, handing off the artifact — in its run record and in the durable docs, not only the machine-side runtime.

Measuring sometimes shows that the plan is too expensive to execute. That is an expected outcome of measurement and a reason to replan, not a failure of the plan, of the operator, or of the item that measured it.

Where a repository maintains an operator-facing derived projection, that projection is where the aggregate belongs: it already states the current human actions and is already reconciled whenever those actions change.

## Batching gated captures

One operator session may satisfy the capture needs of several gated items when all of the following match: source/target/host baselines, scenario/config identity, instrumentation build, and run provenance. A strict "one item, one run" reading of the one-shot contract is what otherwise pushes apart items that wanted evidence from the same run.

Batching does not merge acceptance. Each artifact class still validates independently, and the run record names every roadmap item whose capture needs the session satisfied.

Batching is forbidden where one item's instrumentation materially changes what another observes. When that is uncertain rather than established, run them separately and record why.
