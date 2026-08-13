# agentic-repo-kit roadmap

This is the live backlog for turning successful repository-agent conventions into a reusable, versioned repository policy compiler.

## M0 — usable policy compiler

> A new or existing repository can declare policy profiles, generate a self-contained agent contract, detect drift, and produce a semantic roadmap-normalization packet without copying another repository by hand.

### ARK1 — Bootstrap the first usable kit

- **Status:** Completed and verified
- **Priority:** High
- **Category:** Core tooling
- **Depends on:** none
- **Problem / question:** Extract the reusable process learned from the Ascendancy bootstrap into a small installable tool rather than a GitHub template or copy/paste convention.
- **Known evidence:** Merged PR `kaaburgh/agentic-repo-kit#1` delivered the v0.1.0 compiler and passed its unit/CI/self-check validation.
- **Acceptance:**
  - dependency-free Python CLI exposes `inspect`, `profiles`, `bootstrap`, `check`, `upgrade`, and `normalize-roadmap`;
  - generated contracts are versioned by `.agentic-repo.toml` and `.agentic-repo.lock.json`;
  - policy is composable from domain profiles rather than one universal `AGENTS.md`;
  - project-specific policy can be supplied through local fragment files without forking the kit;
  - generated files refuse unsafe overwrite by default and `upgrade` touches only managed files;
  - tests cover bootstrap, drift detection, overwrite safety, profiles, and semantic packet generation;
  - this repository dogfoods its own `core` profile and passes `agentic-repo check`.
- **Artifacts / docs:** `README.md`, `agentic_repo_kit/`, `schema/`, `examples/`, `tests/`
- **Estimated scope:** Medium

## M1 — real repository dogfood

> The kit can bootstrap a second repository with materially different domain rules, and lessons from that application are folded back into generic/profile layers rather than patched in the target repository blindly.

### ARK2 — Bootstrap bb-shadPS4-correctness-instrumentation

- **Status:** Completed and verified
- **Priority:** High
- **Category:** Dogfood / emulator + graphics
- **Depends on:** ARK1
- **Problem / question:** Apply the kit to `kaaburgh/bb-shadPS4-correctness-instrumentation` using `core + reverse-engineering + proprietary-target + emulator + graphics + upstream-first`.
- **Known evidence:** Merged target PR `kaaburgh/bb-shadPS4-correctness-instrumentation#1` compiled the self-contained contract with the intended profiles, preserved the milestone-level roadmap unchanged, and added project-local provenance policy rather than editing managed output.
- **Acceptance:** bootstrap PR contains the self-contained agent contract without rewriting the project roadmap; any generic deficiencies discovered are fixed in this repository first or in a clearly linked follow-up.
- **Artifacts / docs:** target PR #1; BB `.agentic-repo.toml`, lock, generated policy, and project-local baseline fragment
- **Estimated scope:** Small/Medium

### ARK3 — Normalize the Bloodborne/shadPS4 roadmap

- **Status:** Completed and verified
- **Priority:** High
- **Category:** Dogfood / roadmap compiler
- **Depends on:** ARK2
- **Problem / question:** Turn the milestone-level roadmap into dependency-aware, agent-sized correctness/instrumentation work without inventing emulator or game facts.
- **Known evidence:** Merged target PR `kaaburgh/bb-shadPS4-correctness-instrumentation#2` produced 34 bounded items with explicit dependencies/execution gates, reconciled review-discovered dependency defects, and kept runtime facts explicitly unknown.
- **Acceptance:** the target roadmap can drive one bounded PR at a time and records emulator commit, title build, and host GPU/backend provenance where relevant.
- **Artifacts / docs:** target PR #2 and normalized BB `ROADMAP.md`
- **Estimated scope:** Medium

## M2 — constrained-environment portability

> A repository contract must distinguish a project capability from the capabilities of one sandbox. Restricted network/egress or missing package managers should produce a bounded operator handoff, not an unsupported declaration that the task or capability is impossible.

### ARK4 — Add generic operator-handoff policy

- **Status:** Completed and verified
- **Priority:** High
- **Category:** Core policy / constrained environments
- **Depends on:** ARK3
- **Problem / question:** How should every generated contract behave when a required tool or capability cannot be acquired in the current agent environment because of sandbox, network/egress, package-manager, permission, platform, or similar constraints?
- **Known evidence:** BB dogfood exposed that the v0.1.0 `core` contract has cloud/gated execution guidance but no generic rule that failure to acquire a tool in one sandbox is not evidence that the capability is unavailable to the project. `ascendancy-auto-management` already carries a project-local operator-handoff rule that demonstrates the desired behavior.
- **Implementation evidence:** The ARK4 branch adds the generic rule to `core`, aligns the execution playbook and roadmap-authoring guidance, bumps tool/package version to 0.1.1 without changing `kit_version = 1`, regenerates this repository's managed core contract, and adds focused bootstrap/upgrade regression tests. GitHub Actions CI run #11 passed editable install, all 26 unit tests, and `python -m agentic_repo_kit check .`; the generated dogfood contract is consistent.
- **Proposed direction after evidence:** Put the generic semantics in `core`, keep project-specific evidence/licensing restrictions in local/domain policy, and align roadmap execution guidance so a failed acquisition alone cannot justify `LOCAL ONLY`.
- **Validation / acceptance:**
  - generated `AGENTS.md` says a missing tool in one environment is not evidence that the project capability or task is impossible;
  - agents first prefer a reasonable bounded in-project tool/capability when appropriate, then normal install/download/bootstrap/attached-artifact paths;
  - environment acquisition failure blocks only the dependent line of work; independent work continues;
  - operator handoff records the exact capability/tool, relevant version/platform, why it is required, attempted acquisition paths, and concrete failures;
  - absence of an immediately available operator does not authorize idling or abandoning independent work; the bounded blocker is preserved for handoff;
  - operator-provided generic tools/artifacts remain subject to repository-specific safety/evidence rules rather than bypassing them;
  - failure to acquire a tool in one sandbox is explicitly insufficient, by itself, to classify work `LOCAL ONLY`;
  - the operational playbook and roadmap-authoring environment guidance are consistent with the policy;
  - generated-output regression tests cover the new core text and `upgrade` propagation while preserving unmanaged/local inputs;
  - the repository dogfoods the new generated core contract and `agentic-repo check` passes;
  - because generated policy semantics change without a format/schema break, bump the tool/package patch version while keeping `kit_version = 1`.
- **Artifacts / docs:** `agentic_repo_kit/profiles/core/`, roadmap-authoring template, generated dogfood files, tests, package version
- **Estimated scope:** Small/Medium

### ARK5 — Dogfood operator-handoff upgrade in BB

- **Status:** Completed and verified
- **Priority:** High
- **Category:** Dogfood / upgrade path
- **Depends on:** ARK4
- **Problem / question:** Does a real repository created with v0.1.0 receive the generic operator-handoff policy cleanly through `agentic-repo upgrade` without overwriting its project-local policy or semantic roadmap?
- **Known evidence:** Merged target PR `kaaburgh/bb-shadPS4-correctness-instrumentation#3` upgraded the generated contract from tool v0.1.0 to v0.1.1 using the merged ARK4 upgrade path. The dry-run/check produced exactly four managed changes (`AGENTS.md`, `docs/agent-playbook.md`, `docs/roadmap-authoring.md`, lock), preserved project-local policy and roadmap content, and `agentic-repo check` passed. The actual GitHub target diff independently contained only those four managed files; BB PR #3 rebase-merged as commit `e705711c35241d19ac6e3a4682913ec0bea4bb14`.
- **Result / information gained:** The existing format-1 ownership/upgrade model is sufficient for this policy-only patch release: local inputs and semantic roadmap remain outside managed replacement, while new core policy and tool-version metadata propagate deterministically. No ARK4 follow-up defect was required.
- **Validation / acceptance:**
  - target change is produced by `agentic-repo upgrade`, not hand-editing generated files;
  - BB project-local baseline policy and normalized `ROADMAP.md` remain unchanged unless an independently justified reconciliation is required;
  - only expected managed outputs/lock change for the generic policy/version update;
  - upgraded target passes `agentic-repo check` with the merged kit;
  - the target PR documents the exact kit commit/tool version used and the observed upgrade diff.
- **Artifacts / docs:** BB PR #3 and merged BB commit `e705711c35241d19ac6e3a4682913ec0bea4bb14`
- **Estimated scope:** Small

## M3 — evidence engineering from production RE dogfood

> Reusable RE profiles should protect not only patch safety but also the integrity of the evidence used to discover and justify a patch.

### ARK6 — Add reverse-engineering evidence integrity contract

- **Status:** Completed and verified
- **Priority:** High
- **Category:** Reverse engineering / evidence integrity
- **Depends on:** ARK5
- **Problem / question:** Which Ascendancy review lessons about independent validation, derived analysis artifacts, ambiguity, and ABI inference are generic enough to become reusable reverse-engineering policy?
- **Known evidence:** `ascendancy-auto-management` CF2/T2/RE1/RE2 reviews exposed four recurring failure modes: circular validation of a derived mapping, stale or semantically incompatible machine artifacts, arbitrary identity assignment under duplicate/ambiguous matches, and argument interpretation based on an assumed compiler ABI rather than observed call behavior.
- **Implementation evidence:** The ARK6 branch strengthens the `reverse-engineering` profile and experiment template with independent-oracle rules, all-material-input/schema/producer provenance for machine-readable evidence, fail-closed stale-data handling, explicit ambiguous/unmapped outcomes, and observed ABI evidence. `native-binary-patching` receives the corresponding hook/trampoline ABI boundary. Focused generated-contract tests cover each rule. Self-review widened provenance from a single target input to all material inputs; automated review independently found the stale ARK4 `0.1.1` test assertion, which was replaced with the invariant `lock.tool_version == package __version__`. Tool/package version is 0.1.2 while `kit_version = 1` remains unchanged.
- **Validation evidence:** GitHub Actions CI run `31676500815` on review-corrected head `e3e6a96623e179048df6c4877a874d7de522c226` passed editable install, the full unit suite, and `python -m agentic_repo_kit check .`. The PR diff was reviewed after opening; no target-specific policy or ARK7–ARK9 implementation was introduced.
- **Validation / acceptance:**
  - generated RE policy rejects circular self-validation as independent evidence and distinguishes internal consistency from independent corroboration;
  - derived machine-readable RE artifacts carry schema, all material input identities/hashes, and producer/analysis-model provenance sufficient to reject stale or incompatible evidence;
  - ambiguous/duplicate matches remain machine-visible as ambiguous or unmapped rather than being resolved by arbitrary ordering or fuzzy tie-breaks;
  - ABI/calling-convention claims used for argument interpretation or hook design require direct target evidence when practical;
  - reproducible experiment guidance includes setup/tool versions, differentiating outcomes, artifact names, evidence/confidence, and the next question;
  - focused tests prove the selected profiles compile those rules into generated `AGENTS.md`, playbook, PR template, and experiment docs;
  - full unit tests and `python -m agentic_repo_kit check .` pass;
  - policy semantics change without a format/schema break, so the package patch version advances while `kit_version = 1` remains stable.
- **Artifacts / docs:** `agentic_repo_kit/profiles/reverse-engineering/`, `agentic_repo_kit/profiles/native-binary-patching/`, experiment template, tests, package version
- **Estimated scope:** Small/Medium

### ARK7 — Add reproducible target-experiment contract

- **Status:** Completed and verified
- **Priority:** High
- **Category:** Reverse engineering / runtime evidence
- **Depends on:** ARK6
- **Problem / question:** Which runtime-harness lessons from Ascendancy CF3/CF4 are generic enough to prevent a target experiment from passing on mere liveness, incidental visual change, harness success, or mutation of the supplied evidence tree?
- **Known evidence:** Ascendancy runtime dogfood separated debugger/input/capture capability from exact-target behavior, rejected mode-then-crash and generic frame-change false positives, added semantic expected-screen oracles and bounded execution, and kept maintainer-supplied proprietary runtime inputs immutable while emitting sanitized detached evidence.
- **Implementation evidence:** The ARK7 branch adds semantic target-run oracles, explicit termination/runtime bounds, detached run provenance, and capability-vs-target evidence separation to `reverse-engineering`; adds immutable verified input, isolated working-copy/overlay, sanitization, no-payload run-record rules, and standalone schema/version requirements to `proprietary-target`; and makes graphics acceptance oracles checkpoint/state-specific rather than accepting generic frame activity. Self-review caught the missing standalone run-manifest schema rule. Codex review caught two brittle focused assertions; both were aligned to the normative profile invariants rather than weakening policy. Tool/package version is 0.1.3 while `kit_version = 1` remains unchanged.
- **Validation evidence:** GitHub Actions CI run `31677335349` / run #29 passed on review-corrected head `82dd202b4f227ba9636ec026dde13772bd81681b`: editable install, full unit suite, and `python -m agentic_repo_kit check .` all succeeded.
- **Validation / acceptance:**
  - target-run success/failure is defined by an oracle that directly distinguishes the claimed semantic state/behavior rather than generic activity;
  - waits/retries/actions/captures/log volume/overall runtime and termination semantics are bounded where relevant;
  - synthetic/redistributable controls prove harness capability only and cannot be promoted to exact-target runtime claims;
  - proprietary target/fixture inputs are identity-verified and kept immutable, with writable execution isolated to a copy/overlay/work directory;
  - detached run records have an explicit schema/version and preserve target/fixture, scenario/config, harness/tool, material environment, termination, oracle, and artifact provenance without redistributing proprietary payloads;
  - artifacts sanitize private paths, credentials, user identifiers, and unrelated host data;
  - graphics validation requires checkpoint/state-specific evidence where global frame/hash deltas could produce false positives;
  - focused profile-generation tests and the full unit suite pass;
  - `python -m agentic_repo_kit check .` passes and package patch version advances without a format/schema break.
- **Artifacts / docs:** `agentic_repo_kit/profiles/reverse-engineering/`, `agentic_repo_kit/profiles/proprietary-target/`, `agentic_repo_kit/profiles/graphics/`, tests, package version
- **Estimated scope:** Small/Medium

### ARK8 — Add optional blind-research profile

- **Status:** Completed and verified
- **Priority:** High
- **Category:** Reverse engineering / research provenance
- **Depends on:** ARK7
- **Problem / question:** Can the blind-RE provenance mechanics proven in Ascendancy become an opt-in reusable profile without imposing blind research on ordinary reverse-engineering repositories or hardcoding a project milestone/unlock name?
- **Known evidence:** Ascendancy's blind-research policy required a supported evidence boundary, separated `clean`/`contaminated`/`external-assisted` provenance from evidence class, prevented accidental disclosure from becoming blind success after corroboration, and allowed external target-specific research only after the independent result or through a documented bounded rescue.
- **Implementation evidence:** The ARK8 branch adds a new orthogonal `blind-research` profile with generated agent/playbook/PR fragments. The profile requires projects to define their own durable blind gate/unlock boundary, excludes target-specific recovered shortcuts while permitting general tooling research, treats unsupported repository history as outside the default supported state, defines persistent contamination and bounded rescue semantics, separates post-blind comparison from the historical blind record, and covers operator-provided artifacts that embed target-specific recovered knowledge. README/profile discovery are updated. Self-review found that the first Ascendancy example opted in without defining its required local gate; the example now includes and references a bounded project-local M1 gate/rescue fragment. Codex review found a focused wording mismatch on post-blind comparison; current profile wording matches the asserted invariant. Tool/package version is 0.1.4 while `kit_version = 1` remains unchanged.
- **Validation evidence:** GitHub Actions CI run `31677943666` / run #35 passed on review-corrected head `baf9105deae4f7eeb40f5d97c287f239db640c5b`: editable install, full unit suite, and `python -m agentic_repo_kit check .` all succeeded.
- **Validation / acceptance:**
  - `blind-research` is a discoverable opt-in profile and ordinary `reverse-engineering` does not receive it implicitly;
  - the project must define a durable blind gate/unlock boundary; the profile does not hardcode `M1` or another milestone;
  - allowed primary evidence and prohibited target-specific recovered source classes are distinguished without blocking general tooling research;
  - default supported repository state is current mainline plus branch/PR, while unsupported history cannot silently supply target answers;
  - provenance modifiers remain separate from evidence class and include `clean`, `contaminated`, and `external-assisted` semantics;
  - accidental disclosure remains contaminated even after independent correctness corroboration;
  - pre-unlock rescue requires a prior durable blocker/negative result plus a bounded durable maintainer unlock and does not generalize;
  - post-blind comparison preserves the independent result and records agreements/disagreements separately;
  - operator-provided generic tools remain usable while target-specific recovered artifacts follow the same contamination/rescue boundary;
  - focused profile-generation tests, full unit suite, and `python -m agentic_repo_kit check .` pass;
  - package patch version advances without a config/lock format break.
- **Artifacts / docs:** `agentic_repo_kit/profiles/blind-research/`, README, Ascendancy example + local gate fragment, focused tests, package version
- **Estimated scope:** Small/Medium

### ARK9 — Add structural roadmap and evidence-CI robustness checks

- **Status:** Implemented, validation incomplete
- **Priority:** High
- **Category:** Core tooling / validation
- **Depends on:** ARK8
- **Problem / question:** Which roadmap and CI invariants have become stable enough through Ascendancy and BB dogfood to validate mechanically without pretending that semantic dependency correctness or target evidence can be inferred by the CLI?
- **Known evidence:** Both dogfood repositories now use durable ID-bearing dependency roadmaps, but with two legitimate Markdown shapes (`## ID — ...` plus standalone `Status` in Ascendancy and `### ID — ...` plus compact `Status / priority / execution` in BB). Ascendancy review also exposed that an evidence-producing regression can become falsely reassuring if path filters omit a shared producer/parser/schema/manifest/config dependency.
- **Implementation evidence:** This branch adds a dependency-free Markdown roadmap parser/validator integrated into `agentic-repo check`, validates unique IDs, required status/dependency semantics, dependency references and DAG structure only after structured items exist, preserves milestone-only pre-normalization compatibility, accepts both established dogfood item/field forms and common exact-ID Markdown wrappers, and documents the semantic boundary. Core policy/playbook/PR guidance now requires evidence-producing CI trigger/filter coverage of all material producer dependencies and prefers the real clean-checkout entry point when acceptance depends on it. Focused tests cover graph failures plus the two dogfood presentation variants. Tool/package version is 0.1.5 while `kit_version = 1` remains unchanged.
- **Validation / acceptance:**
  - milestone-only roadmaps remain valid before semantic normalization;
  - normalized item headings at the established `##`/`###` levels are recognized without treating nested prose headings as items;
  - standalone `Status` and compact `Status / priority / execution` both satisfy the stable status invariant;
  - duplicate IDs/fields, missing status/dependency fields, malformed/unknown/self dependencies, and dependency cycles are reported deterministically;
  - `agentic-repo check` integrates structural validation without claiming semantic readiness/root-cause correctness;
  - normalization guidance requires a post-edit `agentic-repo check`;
  - core agent/playbook/PR policy requires evidence-producing selective CI triggers to cover material producer/parser/schema/manifest/config dependencies;
  - generated dogfood contract/lock are reconciled and package version advances without a config/lock format break;
  - full unit tests and `python -m agentic_repo_kit check .` pass in CI;
  - review verifies the validator against the established Ascendancy and BB roadmap shapes before merge.
- **Artifacts / docs:** `agentic_repo_kit/roadmap.py`, `agentic_repo_kit/operations.py`, core policy/playbook/PR fragments, roadmap-authoring/normalization guidance, README, generated dogfood files, focused tests, package version
- **Estimated scope:** Medium

## Later

- Support safe adoption of repositories that already have hand-written `AGENTS.md`/PR templates instead of requiring an explicit migration step.
- Define versioned profile compatibility/migrations when kit format 2 is needed.
- Decide whether semantic roadmap normalization should remain an agent skill packet or gain optional model-provider integration; do not add an LLM dependency without evidence that it improves the workflow.
