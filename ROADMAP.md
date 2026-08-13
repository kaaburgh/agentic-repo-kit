# agentic-repo-kit roadmap

This is the live backlog for turning successful repository-agent conventions into a reusable, versioned repository policy compiler.

## M0 — usable policy compiler

> A new or existing repository can declare policy profiles, generate a self-contained agent contract, detect drift, and produce a semantic roadmap-normalization packet without copying another repository by hand.

### ARK1 — Bootstrap the first usable kit

- **Status:** Implemented, validation complete on branch
- **Priority:** High
- **Category:** Core tooling
- **Depends on:** none
- **Problem / question:** Extract the reusable process learned from the Ascendancy bootstrap into a small installable tool rather than a GitHub template or copy/paste convention.
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

- **Status:** Open
- **Priority:** High
- **Category:** Dogfood / emulator + graphics
- **Depends on:** ARK1 merged
- **Problem / question:** Apply the kit to `kaaburgh/bb-shadPS4-correctness-instrumentation` using `core + reverse-engineering + proprietary-target + emulator + graphics + upstream-first`.
- **Acceptance:** bootstrap PR contains the self-contained agent contract without rewriting the project roadmap; any generic deficiencies discovered are fixed in this repository first or in a clearly linked follow-up.
- **Artifacts / docs:** target-repository PR plus updates here if the profile model changes
- **Estimated scope:** Small/Medium

### ARK3 — Normalize the Bloodborne/shadPS4 roadmap

- **Status:** GATED
- **Priority:** High
- **Category:** Dogfood / roadmap compiler
- **Depends on:** ARK2
- **Problem / question:** Turn the current milestone-level roadmap into dependency-aware, agent-sized correctness/instrumentation work without inventing emulator or game facts.
- **Acceptance:** the target roadmap can drive one bounded PR at a time and records emulator commit, title build, and host GPU/backend provenance where relevant.
- **Estimated scope:** Medium

## Later

- Support safe adoption of repositories that already have hand-written `AGENTS.md`/PR templates instead of requiring an explicit migration step.
- Define versioned profile compatibility/migrations when kit format 2 is needed.
- Decide whether semantic roadmap normalization should remain an agent skill packet or gain optional model-provider integration; do not add an LLM dependency without evidence that it improves the workflow.
- Add richer structural roadmap validation only after dogfood demonstrates stable syntax worth validating mechanically.
