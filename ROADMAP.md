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
  - target-run success/failure is defined by an oracle that directly distinguishes the claimed target state or behavior rather than generic activity;
  - waits/retries/actions/captures/log volume/overall runtime and termination semantics are bounded where relevant;
  - synthetic/redistributable controls prove harness capability only and cannot be promoted to exact-target runtime claims;
  - proprietary target/fixture inputs are identity-verified and kept immutable, with writable execution isolated to a copy/overlay/work directory;
  - detached run records have an explicit schema/version and preserve target/fixture, scenario/config, harness/tool, material environment, termination, oracle, and artifact provenance without redistributing proprietary payloads;
  - artifacts sanitize private paths, credentials, user identifiers, and unrelated environment data;
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

- **Status:** Completed and verified
- **Priority:** High
- **Category:** Core tooling / validation
- **Depends on:** ARK8
- **Problem / question:** Which roadmap and CI invariants have become stable enough through Ascendancy and BB dogfood to validate mechanically without pretending that semantic dependency correctness or target evidence can be inferred by the CLI?
- **Known evidence:** Both dogfood repositories now use durable ID-bearing dependency roadmaps, but with two legitimate Markdown shapes (`## ID — ...` plus standalone `Status` in Ascendancy and `### ID — ...` plus compact `Status / priority / execution` in BB). Ascendancy review also exposed that an evidence-producing regression can become falsely reassuring if path filters omit a shared producer/parser/schema/manifest/config dependency.
- **Implementation evidence:** ARK9 adds a dependency-free Markdown roadmap parser/validator integrated into `agentic-repo check`, validates unique IDs, required status/dependency semantics, dependency references and DAG structure only after structured items exist, preserves milestone-only pre-normalization compatibility, accepts both established dogfood item/field forms and exact-ID Markdown wrappers, ignores fenced schema examples, and distinguishes fieldless section containers from broken fieldless items. Core policy/playbook/PR guidance requires evidence-producing CI trigger/filter coverage of all material producer dependencies and prefers the real clean-checkout entry point when acceptance depends on it. Self-review found the annotated formatted-ID parser defect that caused the first CI failure. Codex independently reported that P1 plus two P2 gaps: fieldless items could bypass required-field checks and fenced examples could create phantom graph nodes. All three behaviors now have focused regression coverage. Tool/package version is 0.1.5 while `kit_version = 1` remains unchanged.
- **Validation evidence:** GitHub Actions CI run `31703339122` / run #43 passed on review-corrected head `4016e1a1df48ea51917a32163cf952b1186254f8`: editable install succeeded, all 59 unit tests passed, and `python -m agentic_repo_kit check .` reported a consistent contract. The parser was checked against the established Ascendancy and BB roadmap presentation shapes before PR creation; review-discovered wrapper, fieldless-item, and fenced-example cases were corrected before verification.
- **Validation / acceptance:**
  - milestone-only roadmaps remain valid before semantic normalization;
  - normalized item headings at the established `##`/`###` levels are recognized without treating nested prose headings or fieldless section containers as items;
  - standalone `Status` and compact `Status / priority / execution` both satisfy the stable status invariant;
  - duplicate IDs/fields, missing status/dependency fields including fully fieldless broken items, malformed/unknown/self dependencies, and dependency cycles are reported deterministically;
  - fenced Markdown examples do not participate in the roadmap graph;
  - `agentic-repo check` integrates structural validation without claiming semantic readiness or dependency correctness;
  - normalization guidance requires a post-edit `agentic-repo check`;
  - core agent/playbook/PR policy requires evidence-producing selective CI triggers to cover material producer/parser/schema/manifest/config dependencies;
  - generated dogfood contract/lock are reconciled and package version advances without a config/lock format break;
  - full unit tests and `python -m agentic_repo_kit check .` pass in CI;
  - review verifies the validator against the established Ascendancy and BB roadmap shapes before merge.
- **Artifacts / docs:** `agentic_repo_kit/roadmap.py`, `agentic_repo_kit/operations.py`, core policy/playbook/PR fragments, roadmap-authoring/normalization guidance, README, generated dogfood files, focused tests, package version
- **Estimated scope:** Medium

## M4 — distribution and mature repository adoption

> Each tool version is reproducibly obtainable without package-registry access, and repositories with an existing hand-written agent contract can transfer managed ownership to the kit without a destructive `--force` bootstrap.

### ARK10 — Publish every tool version as a GitHub Release

- **Status:** Completed and verified
- **Priority:** High
- **Category:** Distribution / constrained environments
- **Depends on:** ARK9
- **Problem / question:** How can a target repository or restricted agent environment obtain the exact kit version needed for `check`/`upgrade` without depending on package-registry access or an unrestricted GitHub checkout?
- **Known evidence:** Generated target policy is self-contained for agent reading, but `agentic-repo check` and `upgrade` execute the kit's renderer/validator code. BB remains pinned to tool 0.1.1 while current kit development advances independently, and some agent environments have constrained network/egress.
- **Implementation evidence:** ARK10 adds a `main` release workflow that validates package/pyproject/lock version identity, acts only on version-owning pushes, fail-closes on a reused tag that points to a different commit, serializes publication, produces deterministic tar/zip source archives plus SHA-256 checksums, and creates a GitHub Release at the exact version commit. Existing partial releases are checked for the required assets and can repair missing assets on a rerun without moving the version tag. README documents offline/PYTHONPATH consumption and distinguishes self-contained generated policy from the executable checker.
- **Validation evidence:** PR #9 CI run `31710044037` / #46 passed editable install, all 61 unit tests, and `python -m agentic_repo_kit check .`. PR #9 rebase-merged as `bb78345a14a67d0c111f8732f39a577c457d0c85`. The resulting Release workflow run `31710240452` / #1 succeeded and published `v0.1.6` at that exact commit with explicit `agentic-repo-kit-0.1.6.tar.gz`, `agentic-repo-kit-0.1.6.zip`, and `SHA256SUMS` assets.
- **Validation / acceptance:**
  - every future tool/package version merged to `main` creates or confirms a `v<version>` GitHub Release;
  - release identity requires `agentic_repo_kit.__version__`, `pyproject.toml`, and the dogfood lock `tool_version` to agree;
  - a tag/release pointing to a different commit fails closed rather than being silently reused;
  - release assets include deterministic `.tar.gz` and `.zip` source archives plus `SHA256SUMS`;
  - an extracted archive can run `python -m agentic_repo_kit check` or `upgrade` via `PYTHONPATH` without package-registry access;
  - docs explain that target CI needs executable kit code and should pin normal drift checks to the target lock's `tool_version`;
  - focused tests, full unit tests, and `python -m agentic_repo_kit check .` pass;
  - after merge, the actual `v0.1.6` GitHub Release exists and points to the merged release commit with the expected assets.
- **Artifacts / docs:** `.github/workflows/release.yml`, `tests/test_release_lifecycle.py`, README, package version, lock, GitHub Release `v0.1.6`
- **Estimated scope:** Small/Medium

### ARK11 — Safely adopt an existing hand-written repository contract

- **Status:** Completed and verified
- **Priority:** High
- **Category:** Core tooling / migration
- **Depends on:** ARK10
- **Problem / question:** How can a mature repository with hand-written `AGENTS.md`, PR template, playbook, or related policy transfer selected files to kit ownership without `bootstrap --force` silently discarding project-specific rules?
- **Known evidence:** Ascendancy has a mature hand-written contract whose generic parts now substantially map to `core + reverse-engineering + blind-research + proprietary-target + native-binary-patching`, while exact blind gate/adoption baseline and other project facts must remain local. Current `bootstrap` correctly refuses conflicting unmanaged files but offers no first-class migration packet/acceptance transaction.
- **Implementation evidence:** The ARK11 branch adds `agentic-repo adopt` with non-destructive JSON plan mode and explicit `--apply PLAN_ID`. The plan binds tool version, config, roadmap/local-input identities, existing managed-surface hashes/actions, and prospective generated hashes; replacements expose unified diffs and required operator decisions. Apply rejects stale/malformed plans, rechecks reviewed inputs and current/prospective hashes immediately before writes, atomically replaces files, preserves existing POSIX modes/uses readable modes for new files, writes the ownership lock last, and rolls back prior writes on failure. Canonical aliases of generated outputs are rejected as local inputs; plan output cannot overwrite adoption inputs, managed targets, or any existing file. Existing locks route to `upgrade`. Documentation lives in `docs/adoption.md`; tool/package version is 0.1.7 with `kit_version = 1` unchanged.
- **Validation evidence:** Initial PR CI run `31711751625` / #48 passed 68 tests and self-check. Self-review added an immediate pre-write recheck for reviewed roadmap/local inputs. Codex review identified canonical-path aliasing, destructive plan-output collisions, POSIX `0600` replacement modes, and the stale roadmap status; the three code-path defects were corrected with focused regressions. Review-corrected CI run `31712469402` / #53 passed all 72 unit tests and `python -m agentic_repo_kit check .`. Final pre-merge CI run `31712861597` / #54 also passed. PR #10 rebase-merged as `1e708b795e5cc9dd1ea1efcc79f957638ad695cf`; post-merge CI run `31713011698` / #55 succeeded. Release workflow run `31713011752` / #2 succeeded and published `v0.1.7` at that exact commit with `agentic-repo-kit-0.1.7.tar.gz`, `agentic-repo-kit-0.1.7.zip`, and `SHA256SUMS` assets. The Ascendancy-shaped fixture proves that a hand-written contract can transfer to `core + reverse-engineering + blind-research + proprietary-target + native-binary-patching` while a project-local M1 blind gate remains outside managed ownership and is composed into the generated contract.
- **Validation / acceptance:**
  - adoption has a non-destructive default/plan mode that never modifies the repository unless an explicit new `--output` artifact path is requested;
  - the plan identifies existing conflicting managed paths and whether prospective output differs;
  - apply requires an explicit acceptance token bound to the exact plan/input state so repository changes between review and apply fail closed;
  - project-local fragments remain outside managed ownership and are composed into generated output before ownership transfer;
  - adoption is transactional: all writes are preflighted before any managed file or lock changes, managed files are replaced atomically, the lock is written last, and partial writes are rolled back on failure;
  - existing hand-written contract files are not silently discarded; the migration report makes replacement diffs and required operator decisions reviewable;
  - after successful adoption, ordinary `agentic-repo check` and later `upgrade` own only the declared managed files;
  - focused synthetic migration tests include an Ascendancy-shaped fixture with hand-written `AGENTS.md`/PR policy plus local blind gate;
  - full unit tests and self-check pass; package version advances and the release workflow publishes that new version.
- **Artifacts / docs:** `agentic_repo_kit/adoption.py`, adoption CLI, `docs/adoption.md`, safe-adoption tests, Ascendancy-shaped fixture, package version, GitHub Release `v0.1.7`
- **Estimated scope:** Medium

### ARK12 — Publish a pinned executable distribution contract

- **Status:** Completed and verified
- **Priority:** High
- **Category:** Distribution / constrained environments
- **Depends on:** ARK11
- **Problem / question:** Can every consumer repository pin one directly executable, reproducible kit artifact—including its acquisition coordinates and SHA-256—in the lock so online CI and offline operator handoff use the same trust anchor without vendoring the dependency?
- **Known evidence:** BB upgrade to v0.1.7 exposed that source archives solve package-registry independence but consumer repositories still need prose to discover/acquire the checker. Making the kit repository public removed the cross-repository credential requirement while preserving the need for an immutable executable distribution identity.
- **Implementation evidence:** ARK12 adds deterministic `agentic-repo-kit-<version>.pyz` builds, source/wheel distribution metadata, self-hashing identity when executing inside the zipapp, and lock format 2 with `repository`/`release`/`artifact`/`sha256`/`tool_version`. The committed digest metadata is deliberately excluded from the zipapp to avoid cryptographic self-reference. Release publication rebuilds the artifact and fails closed unless its SHA-256 equals the lock digest. Tool/package version is 0.1.8 while config `kit_version = 1` remains unchanged.
- **Validation evidence:** Draft PR #12 used CI as the deterministic builder: all non-placeholder tests passed and produced SHA-256 `7e44e7eb9b81dc3ca357ab98a4f6170bf900bea9673ea27ec831768e7acf5847`; final-head CI #66 passed after the digest was pinned. PR #12 rebase-merged at `f95068f36c839cc2df21cea3067674b3f7679c9a`. Post-merge release testing found two real recovery defects before publication (nested-shell parsing and an invalid history-derived release target); bounded follow-up PRs #13–#15 corrected release recovery to preserve exact version-owning commit identity. Release run #6 then published `v0.1.8` at exact ARK12 commit `f95068f36c839cc2df21cea3067674b3f7679c9a` with `.pyz`, tar/zip, and `SHA256SUMS`; the published `.pyz` digest exactly matches the lock. After the one-time recovery fallback was removed, Release run #7 passed the verification-only existing-tag/digest path with build/create/repair correctly skipped.
- **Validation / acceptance:**
  - deterministic `.pyz` builds are byte-identical across repeated builds from the same source tree;
  - the executable runs normal CLI commands with Python 3.11+ and no package-registry dependency;
  - lock format 2 records exact public repository/release/artifact coordinates and SHA-256 together with tool/config/profile/generated provenance;
  - `bootstrap`, `adopt`, and `upgrade` atomically emit those distribution coordinates as part of the lock;
  - source/wheel mode and zipapp mode render the same distribution identity without embedding the digest metadata into the artifact it describes;
  - the release workflow refuses publication if a rebuilt `.pyz` digest differs from the committed lock digest and verifies/repairs existing assets against that digest;
  - normal version publication preserves the exact version-owning push SHA; explicit recovery requires an exact ancestor `target_sha` rather than guessing from history;
  - offline handoff needs only the artifact because the expected digest is already committed in the consumer lock;
  - `SHA256SUMS` remains a release-level cross-check, not the consumer trust anchor;
  - package/tool version advanced to 0.1.8, lock format advanced to 2, and config `kit_version = 1` remained stable.
- **Artifacts / docs:** `scripts/build_pyz.py`, `agentic_repo_kit/distribution.py`, `agentic_repo_kit/distribution.json`, renderer/lock format 2, release workflow, `docs/distribution.md`, focused tests, GitHub Release `v0.1.8`
- **Estimated scope:** Medium

### ARK13 — Generate the repository contract check workflow

- **Status:** Completed and verified
- **Priority:** High
- **Category:** Core tooling / managed CI
- **Depends on:** ARK12
- **Problem / question:** Can the kit make its own deterministic contract validation a managed target-repository invariant rather than requiring every consumer to hand-author a GitHub Actions workflow?
- **Known evidence:** BB had a valid repo-kit contract but no generic contract-check Actions workflow. ARK12 supplied a public pinned executable plus digest in lock format 2, making a secret-free consumer workflow possible.
- **Implementation evidence:** ARK13 generates and owns `.github/workflows/agentic-repo-check.yml`. The workflow has `contents: read` only, broad pull-request/push triggers with no path filters, validates all lock distribution fields, downloads the exact public `.pyz`, verifies SHA-256 against `distribution.sha256`, and runs `python <artifact>.pyz check .`. It uses current `actions/checkout@v7` and `actions/setup-python@v7`. The workflow itself is a trusted generated path; `check` detects drift and `upgrade` adds/updates a managed copy while refusing an unmarked project-owned conflict. The kit repository alone may deterministically self-build the not-yet-published `.pyz` during a version-bump PR when its lock distribution repository equals `GITHUB_REPOSITORY`; that artifact must still match the committed digest before execution. Tool/package version is 0.1.9 with lock format 2 and config `kit_version = 1` unchanged.
- **Validation evidence:** Before `v0.1.9` existed, the generated workflow exercised the pre-release self-host path and produced final deterministic SHA-256 `79e914bc322873025f41db0ffa118bd037362b77708e4433bb854d8dd42b041e`; managed workflow run #29 then passed Resolve → Acquire → Verify → `check` end-to-end with that digest. Final ARK13 head passed ordinary CI #89 and managed contract workflow #35. PR #16 rebase-merged as `5a2bb177927c0a7ad465cdd2569f93f305a9e896`; post-merge managed check passed and Release #8 published `v0.1.9` at that exact commit with `.pyz` digest `79e914bc322873025f41db0ffa118bd037362b77708e4433bb854d8dd42b041e`. BB dogfood PR #12 then upgraded a real pre-ARK13 repository from lock format 1/tool 0.1.7 to format 2/tool 0.1.9 with exactly two managed changes: the lock and new workflow. BB Agentic repository contract run #3 downloaded the public 44,098-byte v0.1.9 `.pyz` from GitHub (self-host fallback was ineligible), verified the lock digest, and printed `agentic repository contract is consistent`; the independent Bloodborne target-manifest run also passed. BB PR #12 rebase-merged as `51ed6cd235d0ef9223d6e9811b283fe8a02faf7c`. Project-owned BB acquisition guidance was then reconciled through the published v0.1.9 `upgrade`/`check` path and merged in BB PR #13 as `ae52ef93710e03208ab9f223416820c53770d1cf`.
- **Validation / acceptance:**
  - generated workflow uses only coordinates/digest from the committed lock and never resolves a release via `latest`;
  - public acquisition requires no cross-repository secret;
  - SHA-256 is checked against `distribution.sha256` before execution;
  - the workflow runs `python <artifact>.pyz check .` and fails on contract/roadmap drift;
  - the workflow is a trusted generated path, participates in ownership/drift checking, and upgrades transactionally with other managed outputs;
  - a project-owned same-name workflow is not silently overwritten;
  - self-host acquisition is restricted to the distribution repository's own pre-release bootstrap cycle and still requires the lock digest;
  - focused tests cover rendered semantics, drift, upgrade from pre-ARK13 state, and unmanaged-path refusal;
  - BB dogfood receives the workflow through ordinary upgrade and proves the public download/verify/check consumer path in real GitHub Actions;
  - package/tool version advanced to 0.1.9 while config `kit_version = 1` remained stable.
- **Artifacts / docs:** workflow template, generated dogfood workflow, renderer/ownership allowlist, `tests/test_managed_check_workflow.py`, `docs/distribution.md`, package version, GitHub Release `v0.1.9`, BB PRs #12/#13
- **Estimated scope:** Medium

## M5 — unattended execution contract

> A repository can state how an unattended scheduled agent must obtain evidence, write commits, bind review verdicts and report, so that contract lives in the repository rather than in a chat-side prompt that no reviewer can see and no tool can validate.

### ARK14 — Add an unattended-agent-cycle profile

- **Status:** Implemented, validation incomplete
- **Priority:** High
- **Category:** Core policy / unattended execution
- **Depends on:** ARK13
- **Problem / question:** A scheduled ChatGPT task driving `issue → PR → CI → review → fix` needs rules that no current profile states: which write path is sanctioned when there is no working tree, how a review verdict binds to one SHA, what a verdict looks like when author and reviewer share an account, when a run may wait, and what its report must contain. Today those rules live only in the task prompt. Can they become a generated, versioned repository contract?
- **Known evidence:** Live runs against `kaaburgh/kinopub.webos` on 2026-08-17 confirm three independent failure modes that a repository-side contract would remove.
  1. ChatGPT project instructions are **not** visible to a scheduled task. Two consecutive runs reported the prompt's own canary as `POLICY LAYER: MISSING` and fell back to an abbreviated rule set. Repository files are always readable, so the repository is the only reliable carrier.
  2. The prompt named `main`; the repository's default branch is `master`. The run reported this correctly as an instruction defect, but it is a defect a repository-side contract cannot have, because the contract ships with the repository.
  3. Earlier runs against several repositories reported `docs/PROJECT_STATUS.md` missing every cycle because a stale prompt named a file no repository has. A generated contract is checked for drift and cannot drift out of the repository it describes. Additionally, `kaaburgh/bb-shadPS4-correctness-instrumentation#18` establishes the review topology this contract must describe: all 15 reviews carry `state: COMMENTED` because GitHub forbids self-approval, and merge-readiness is signalled by a 👍 reaction on the PR body — from `chatgpt-codex-connector[bot]` for the bot verdict and from the owner account for the human-side verdict.
- **Implementation evidence:** PR #22 adds the discoverable opt-in `unattended-agent-cycle` profile, profile-owned generated `docs/agent-cycle-run.md`, the profile-specific `AGENTS.md` link fragment, trusted ownership/drift handling, and focused selection/drift/pre-ARK14-upgrade/unmanaged-conflict/contract-semantics tests. The generated contract defines permanent runner properties, repository-metadata default-branch discovery, atomic Git-object and bounded per-file write paths, exact-SHA CI/review/reaction binding, shared-account review classification, thread disposition, validation execution levels, and cycle reporting while leaving approval/override eligibility outside repository-carried policy. Tool/package version is 0.1.13 with `kit_version = 1` unchanged.
- **Validation evidence:** On exact implementation head `b442c0545cc14023dc5560af4d740a95d7fe41e7`, CI run `32000467426` passed the full 89-test suite and `python -m agentic_repo_kit check .`; managed contract run `32000467356` also passed. Review-driven hardening resolves the authoritative cycle contract from a trusted default-branch revision (or an externally pinned trusted blob), defines `CYCLE CONTRACT: MISSING` when the contract is absent on the trusted revision so a proposed PR copy cannot self-authorize policy, requires fresh same-source SHA-bearing approval evidence before a PR-body 👍 can be used, permits legitimate no-write cycles, and keeps both write paths conflict-safe: CAS/concurrency outcomes never authorize Path B fallback, while Path B requires mechanism-level atomic failures plus expected branch/blob/absence preconditions and intermediate-head verification. The deterministic v0.1.13 `.pyz` SHA-256 `b1b7b23f1082dd3998cf01f6335a571aa695eb422a99aa1809e8e5770317c985` is pinned in distribution metadata and the dogfood lock. Release publication remains pending merge.
- **Hypotheses:** The rules are orthogonal to domain. They do not belong in `core` wholesale, because they assume an unattended runner and a shared-account review topology that an ordinary interactive repository does not have. Two clauses inside them — evidence-over-mechanism and the validation execution level — are generic enough for `core` and are proposed as a follow-up rather than folded in here.
- **Proposed direction after evidence:** Add an opt-in orthogonal profile `unattended-agent-cycle` generating one managed file `docs/agent-cycle-run.md`, referenced from `AGENTS.md` alongside the playbook. Keep in the chat-side prompt only what must not be stored where the agent can write: the anti-self-approval prohibitions, the run-scoped review switch and the override acceptance rules.
- **Compatibility / safety:** Generated policy that the executing agent can also modify is a self-referential trust boundary. The contract must therefore state that changing it is ordinary roadmap work requiring its own issue, PR and review, and the chat-side prompt must forbid same-run edits to it. Do not move the anti-self-approval prohibitions into the repository.
- **Validation / acceptance:**
  - `unattended-agent-cycle` is a discoverable opt-in profile; repositories that do not select it receive no unattended-run policy;
  - the profile generates and owns `docs/agent-cycle-run.md`, participates in ownership and drift checking, upgrades transactionally, and refuses to overwrite an unmarked project-owned file;
  - generated `AGENTS.md` links the new document where the profile is selected, and does not when it is not;
  - the contract states that missing DNS, a missing CLI client, a missing working tree and a non-first-class OS are permanent runner properties and never a reason for an empty cycle;
  - the contract requires reading the default branch from repository metadata rather than assuming `main`;
  - the contract defines two pre-approved write paths, prefers atomic Git-object construction, and permits per-file writes only after the atomic path is refused twice in the same run, requiring every intermediate SHA and an explicit statement that atomicity was lost;
  - the contract binds every verdict, CI status and reaction to one exact SHA, forbids waiting for an `APPROVED` review in a shared-account topology, and defines the PR-body 👍 as the approval signal distinguished by reacting account;
  - the contract states that owner-account reviews are not distinguishable by author and must be classified by content;
  - the contract defines thread handling including the addressed / partially addressed / disputed split and forbids resolving an unaddressed thread;
  - the contract's report section requires evidence mechanism, validation execution level, write path used, resolved and open threads, every `unknown`, and an `INSTRUCTION DEFECTS` section;
  - focused generation tests cover profile selection, the `AGENTS.md` link, drift detection, and upgrade from a pre-ARK14 lock;
  - full unit tests and `python -m agentic_repo_kit check .` pass;
  - the package patch version advances while config `kit_version = 1` stays stable, and the release workflow publishes it.
- **Artifacts / docs:** `agentic_repo_kit/profiles/unattended-agent-cycle/`, generated `docs/agent-cycle-run.md`, `AGENTS.md` link fragment, README profile list, focused tests, package version
- **Estimated scope:** Medium

### ARK15 — Dogfood the unattended contract in a live loop repository

- **Status:** Open
- **Priority:** High
- **Category:** Dogfood / unattended execution
- **Depends on:** ARK14
- **Problem / question:** Does a repository that receives `docs/agent-cycle-run.md` through ordinary `upgrade` actually change unattended-run behaviour, and does the run prompt shrink to the switch plus the prohibitions without losing discipline?
- **Known evidence:** `kinopub.webos` currently produces runs that are correct in form but degraded in substance, because the policy layer never loads. Its default branch is `master`, which independently exercises the no-`main` requirement. ARK15 preflight on 2026-08-17 against `master` head `8f71ddbfd9ee1ffa23d3c857578f2e9a2aa258d6` found no `.agentic-repo.toml` or `.agentic-repo.lock.json`; `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, and `docs/agent-playbook.md` are hand-written, so there is no managed baseline on which ordinary `upgrade` can operate. The existing scheduled task `Kinopub agentic cycle` is disabled and still carries the thick pre-ARK14 prompt. ARK14 also proves that selecting `unattended-agent-cycle` necessarily changes generated `AGENTS.md` to add the cycle-contract link, so the earlier expectation of only a new document plus lock was impossible.
- **Next experiment:** First establish a separately reviewable ARK-managed `core` baseline in `kinopub.webos` with `agentic-repo adopt`, preserving project-specific rules through configured local policy/playbook/PR fragments and proving `agentic-repo check`. After that baseline merges, add `unattended-agent-cycle` to `.agentic-repo.toml` and run ordinary v0.1.13 `upgrade`; review the exact profile-enable diff. Then replace the disabled scheduled task's thick prompt with the thin external switch/prohibition layer, enable it, and compare three consecutive cycles against the pre-ARK14 baseline.
- **Expected information gain:** Whether a safely adopted repository actually reads and obeys repository-carried unattended policy, whether profile enablement remains a bounded deterministic upgrade, and whether any rule silently degrades once it is one document further away than the prompt.
- **Validation / acceptance:**
  - before profile enablement, the target has a reviewed ARK-managed `core` adoption baseline produced through `agentic-repo adopt`; project-specific hand-written policy that must survive is represented through configured local fragments, ownership transfer is explicit, and v0.1.13 `agentic-repo check` passes;
  - the profile-enable change explicitly adds `unattended-agent-cycle` to `.agentic-repo.toml`, and ordinary `upgrade` changes only the expected managed outputs for that selection: generated `AGENTS.md` gains the cycle-contract link, `docs/agent-cycle-run.md` is created, and the lock is updated; no unrelated managed output changes;
  - three consecutive scheduled cycles report a resolved `CYCLE CONTRACT` sha rather than `MISSING`;
  - no cycle reports a missing `docs/PROJECT_STATUS.md`, a `main` assumption, or any other instruction defect originating in the thin prompt;
  - head binding, one-request-per-SHA and no-force-push hold across those cycles;
  - the runner never produces an override token, never reacts to its own PR, and never resolves an unaddressed thread;
  - if the atomic write path is refused, the per-file path is used and reported with every intermediate SHA and the explicit atomicity statement.
- **Artifacts / docs:** target adoption `.agentic-repo.toml`, local policy/playbook/PR fragments, baseline lock/generated contract, profile-enabled config/lock/generated `docs/agent-cycle-run.md`, three cycle reports
- **Estimated scope:** Small/Medium

### Follow-up candidate, not part of ARK14

Two clauses in `docs/agent-cycle-run.md` are generic enough for `core` and would then apply to every generated contract, unattended or not:

- **Evidence over mechanism** — a workflow step naming a specific tool specifies the evidence required, not the mechanism required; any mechanism returning the same fields satisfies it.
- **Validation execution level** — an explicit ladder of reconstructed-local, CI-on-exact-head, and `unknown`, kept separate from the project's evidence classes.

Both overlap the existing `core` sections "Tool availability and operator handoff" and "Validation and claims" and should be reconciled with them rather than appended, so open them as their own item once ARK14 has landed and the wording has survived real cycles.

## Later

- Define versioned config/profile compatibility migrations when `kit_version = 2` is needed.
- Decide whether semantic roadmap normalization should remain an agent skill packet or gain optional model-provider integration; do not add an LLM dependency without evidence that it improves the workflow.
