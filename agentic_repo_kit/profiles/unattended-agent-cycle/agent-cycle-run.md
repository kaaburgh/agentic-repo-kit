{{MARKER}}
# Unattended agent cycle contract

This contract governs unattended scheduled `issue → PR → CI → review → fix` cycles when the `unattended-agent-cycle` profile is selected. It defines evidence, write, review-binding, thread, wait, and reporting semantics. Approval eligibility, override acceptance, and other anti-self-approval controls remain external to this repository-carried contract.

Changing this contract is ordinary roadmap work. A change to the profile or generated contract requires its own issue or roadmap item, PR, validation, and review. An executing cycle must use the committed contract it resolved at the start of the run and must not treat same-run edits as authority for that run.

## Start-of-cycle identity

At the start of every cycle:

1. Read repository metadata and obtain the repository's actual default branch. Never assume the branch is named `main`, `master`, or anything else.
2. Resolve the default-branch head and, when working on a PR, the exact PR head SHA.
3. Resolve `docs/agent-cycle-run.md` from repository contents and record its Git blob SHA as `CYCLE CONTRACT`.
4. Record the evidence mechanism used to obtain each identity, such as repository API, Git object API, CLI, or reconstructed local checkout.

A later head change invalidates current-head claims made against the earlier SHA. Preserve earlier evidence as historical evidence instead of silently rebinding it.

## Permanent runner properties and useful work

Missing DNS, a missing CLI client, a missing working tree, and a non-first-class host OS are runner properties, not reasons for an empty cycle. Record them when relevant, choose a sanctioned mechanism that can still produce the required evidence, and continue every independent line of work that remains executable.

A cycle may wait only when all currently executable independent work is exhausted and a named external condition is already in flight, such as CI or review for one exact head SHA. The report must name that condition and SHA. A permanent runner property by itself never justifies waiting or an empty cycle.

## Pre-approved write paths

There are exactly two pre-approved repository write paths for unattended cycles.

### Path A — atomic Git-object construction

Prefer this path. Create the required blobs, construct one tree from the intended base tree, create one commit, and advance the branch ref once with a fast-forward update. Verify the resulting branch head equals the created commit before requesting CI or review.

### Path B — per-file repository writes

Use per-file writes only after Path A has been refused or rejected twice in the same run by the available repository mechanism. Record both failed atomic attempts and their concrete errors before falling back.

Each successful per-file write may create a new commit. Record every intermediate commit SHA in order, then resolve and report the final branch head. The report must state explicitly: `ATOMICITY: LOST — per-file fallback used`.

Do not rewrite a previously reviewed head to make new changes appear under the old SHA. A review request, CI result, reaction, or verdict is evidence only for the exact SHA it names.

## Exact-head binding

Bind every CI status, review submission, review request, review-thread disposition, reaction, and merge-readiness verdict to one exact commit SHA.

When the PR head changes:

- prior CI remains evidence for the prior head only;
- prior review verdicts remain evidence for the prior head only;
- prior reactions remain evidence for the prior head only;
- request review for the new SHA when review is required; do not repeatedly request the same reviewer for the same SHA merely because another cycle ran.

Report `unknown` rather than inheriting an unbound or stale verdict.

## Shared-account review topology

In a topology where author and reviewer activity can share an owner account, do not wait for GitHub review state `APPROVED` as the merge-readiness oracle. GitHub may expose valid review feedback only as `COMMENTED` in that topology.

Treat a 👍 reaction on the PR body as the approval signal only when its reacting account is the designated verdict source for the workflow. Distinguish bot-side and human-side verdicts by the reacting account that produced the reaction, and bind the reaction observation to the exact PR head SHA observed at the same time.

Owner-account review submissions are not distinguishable by author identity alone. Classify them by review content and thread context. A `COMMENTED` state is transport metadata, not by itself approval or rejection.

## Review threads

Classify each review thread against the current head as one of:

- **addressed** — the current head fully incorporates the requested correction or the evidence requested by the thread; after verifying that fact, the thread may be resolved;
- **partially addressed** — some requested work is present but a material part remains; reply with what changed and what remains, and keep the thread open;
- **disputed** — the requested change is intentionally not adopted; reply with the evidence and rationale, and keep the thread open unless the reviewer explicitly accepts the disposition;
- **unaddressed** — no adequate correction or disposition exists; keep the thread open.

Never resolve an unaddressed thread. Do not infer resolution merely from a new commit or a generic green CI result.

## Validation execution level

Report validation execution separately from the project's evidence classes using one of these levels:

- `reconstructed-local` — validation ran in a reconstructed, synthetic, or otherwise non-authoritative local environment;
- `CI-on-exact-head` — CI ran against and is explicitly bound to the exact reported head SHA;
- `unknown` — the execution level cannot be established from available evidence.

A stronger evidence class does not upgrade an unknown execution level, and local reconstruction does not become exact-head CI merely because equivalent commands were run.

## Cycle report

Every cycle report must include enough evidence to reconstruct what happened without chat history:

- `CYCLE CONTRACT`: the resolved Git blob SHA for this document;
- repository default branch and exact starting/final head SHA;
- evidence mechanism used for repository metadata, file reads, CI, reviews, reactions, and writes;
- validation execution level for every validation claim;
- write path used (`atomic Git-object` or `per-file fallback`), including both atomic-path refusal errors before fallback and every intermediate SHA when Path B was used;
- exact-SHA bindings for CI statuses, review requests, review verdicts, and PR-body reactions;
- review threads grouped as resolved/addressed and open/partially-addressed/disputed/unaddressed;
- every material `unknown` that remains;
- an `INSTRUCTION DEFECTS` section naming stale, contradictory, impossible, or repository-inapplicable instructions discovered during the run. Use `none` only when none were observed.

If Path B was used, include the explicit atomicity-loss statement required above. If the cycle waited, name the exact external condition and SHA it was waiting on.
