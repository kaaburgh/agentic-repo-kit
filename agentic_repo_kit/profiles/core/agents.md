## Source of truth and scope

When sources disagree, prefer: the current task and explicit maintainer decisions; current reproducible evidence; current source/tests/tool output; the live roadmap; durable project documentation; then historical notes. Do not implement an old plan merely because it exists.

`ROADMAP.md` is live project state. A PR must update its selected item when the PR changes status, evidence, dependencies, sequencing, compatibility, direction, or acceptance criteria. Preserve negative results and disproved premises instead of silently deleting the reasoning.

For normalized roadmap items, keep IDs unique and dependency references valid and acyclic. Structural validation checks graph consistency only; it does not replace evidence-based review of whether the dependencies are semantically correct.

Keep work bounded. Do not opportunistically absorb adjacent roadmap items unless inseparable. A PR must be understandable without chat history.

An item that plainly will not fit in one PR declares `Slice budget: k/N` and its remaining slices. Do not exceed that budget silently: either split the item into separate IDs, or re-budget explicitly and state what changed to justify it. Incrementing the budget without that justification is the failure it exists to catch.

## Vertical slice before formalisation

For any producer, instrumentation, or contract item, the first slice must produce one real end-to-end output on the narrowest path that can carry one. Schemas, conformance vectors, admission contracts, and cross-language checks come after there is something to conform to.

This is an order of operations, not a lower bar. It does not weaken any evidence or provenance requirement, does not permit synthetic evidence to be presented as runtime evidence, and is never a reason to skip a contract — only a reason to sequence it after the first real output.

It is also not a reason to idle. Where the narrow end-to-end path is genuinely gated on an operator or an unavailable capability, the handoff rules below apply and formalisation while properly blocked is legitimate work. The rule addresses the case where the narrow path was available and formalisation was chosen over it.

Take that case seriously, because it is generated rather than accidental: when runtime access is missing and the bar for rigour is high, formalisation is the action that is always available and always passes review. A sequence of individually correct, bounded, honestly labelled contract slices that never emitted anything is the expected outcome of selecting the best available item every time, not evidence of bad judgement in any one of them. It is visible only in the sequence, so state which end-to-end output an item's first slice produces, and say so explicitly when the answer is none.

## Operator-facing derived projections

The authoritative roadmap remains the single source of truth for planning state: project state, dependencies, readiness, evidence, acceptance criteria, and sequencing. A repository may also maintain a short operator-facing checklist or handoff document that projects the current actions a human needs to take. The projection may carry procedural detail from linked durable docs, scripts, or tooling, but those sources supply procedure rather than competing planning state. Treat the operator-facing document as a derived projection, never as a second source of truth.

If a PR changes current operator actions or instructions, reconcile any existing operator-facing projection in the same PR, whether the change comes from roadmap state or from the procedure that implements it. This includes changes to ready/current `LOCAL ONLY` work, operator handoffs, `Next experiment`, required inputs or steps, acceptance or collection requirements, the appearance or disappearance of a local step, and referenced commands, flags, preflight steps, scripts, or packaging/collection procedure.

Keep the projection limited to current actionable human work. Completed items, blocked downstream items, and purely cloud-executable items do not become operator checklist entries merely because they exist in the roadmap. If the projection disagrees with the roadmap about planning state, the roadmap wins; if its procedural detail is stale relative to the durable docs/scripts it summarizes, correct the projection.

The projection's path, format, and maintenance mechanism are project-specific and may be declared through local policy or future configuration. Do not assume a file is named `NEXT-STEPS.md`. Unless an explicit projection/reconciliation mechanism exists, `agentic-repo check` must not be treated as semantically deriving or validating an arbitrary operator checklist from roadmap prose.

## Validation and claims

Run the narrowest meaningful checks first, then broader checks warranted by the change. State exactly what ran and what did not. Compilation, linting, or synthetic tests do not establish real-target behavior.

When an evidence-producing CI job uses selective triggers, include every material producer, parser, schema, manifest, and configuration input that can change the validated output. Use broader triggering when a narrow dependency set cannot be maintained reliably.

A rule described as enforced must be enforced by a property of the data, not by a field in which the producer declares its own compliance. Comparing a self-declared label reports conformance that was never checked, and reads to every later agent as though it had been. Where a rule can only be judged by a person, say so where the rule is written and wherever a validator would otherwise appear to cover it.

Do not invent commands, targets, performance numbers, supported versions, or architecture details. If an important premise is unknown, turn it into an observation or experiment before implementation.

## Tool availability and operator handoff

A missing tool or capability in one agent environment is **not** evidence that the capability is unavailable to the project or that the task is impossible. Escalate environment-specific acquisition failures as bounded operator handoffs instead of turning them into unsupported project conclusions.

Before escalating an unavailable capability, confirm that it is required by the task's acceptance or evidence needs rather than merely a useful optional cross-check.

When a required capability is missing:

- first decide whether a small in-project tool or script can provide the required evidence safely and within the current task scope; prefer that when it is a reasonable bounded solution rather than silently substituting a weaker analysis method;
- otherwise try the normal installation, download, bootstrap, package-manager, or attached-artifact paths available in the current environment;
- if sandbox, network/egress, package-manager, permission, platform, or similar constraints block acquisition, pause only the line of work that requires that capability and continue every independent line of work;
- report the exact missing tool/capability, relevant version/platform requirements, why it is required, acquisition paths already attempted, and the concrete failures so an operator can supply or enable the missing piece;
- if no operator is available in the current session, preserve the bounded blocker and continue independent work rather than idling or declaring the entire task impossible;
- treat operator-provided tools or artifacts as inputs subject to the repository's existing safety, licensing, provenance, and evidence rules; an operator handoff does not override stricter project/domain policy;
- preserve reusable acquisition/bootstrap knowledge when the blocker is resolved, and record important negative acquisition results when they would otherwise be rediscovered.

Failure to acquire a tool inside one sandbox is not, by itself, sufficient evidence to classify work `LOCAL ONLY`, mark the underlying capability unavailable, or close the task as impossible.
