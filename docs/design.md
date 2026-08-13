# Design

## Boundary

The kit is a **repository policy compiler**, not a remote policy dependency. A target repository keeps a self-contained generated snapshot so coding agents can work from the checkout alone and reviewers can see policy changes in normal diffs.

The model has three layers:

1. `core` — process invariants useful across domains;
2. composable domain profiles — RE, proprietary targets, native patching, emulators, graphics, upstream-first;
3. project-owned facts and local fragments — commands, architecture, product decisions, supported versions and other repository-specific knowledge.

A rule belongs in core only if it should apply to materially different repositories. A rule belongs in a profile if it is domain-specific but reusable. Target facts stay in the target repository.

## Deterministic vs semantic operations

`inspect`, `bootstrap`, `check`, and `upgrade` are deterministic filesystem operations. They can be unit-tested and must fail closed around unknown profiles, unsupported config formats, unmanaged overwrite conflicts, missing local inputs, and generated drift.

Roadmap normalization is semantic. The tool does not claim it can deterministically infer dependencies, root causes, experiments, or acceptance criteria from prose milestones. `normalize-roadmap` creates a self-contained agent packet containing repository inspection and the canonical procedure. A capable coding agent performs the reasoning and commits the resulting roadmap in a separate PR.

## Ownership and upgrades

Generated files carry a marker. Direct project customization belongs in `[local]` fragment files so a later `upgrade` can re-render policy without losing local rules.

`bootstrap` refuses any differing existing output by default. `--force` is an explicit migration escape hatch. `upgrade` is narrower: it may replace only code-known generated output paths carrying the generated marker (plus the lock file), and may create missing generated files. An unmanaged conflict fails closed.

The lock records the installed tool version, config format version, selected profiles and SHA-256 of each generated output. It is **provenance/state, not an ownership authority**: repository contents can forge or corrupt the lock, so its manifest cannot authorize overwriting or deleting arbitrary paths. Obsolete deletion is constrained by a code-owned generated-output allowlist and the generated marker. A manifest entry outside that allowlist fails closed before mutation.

The current MVP supports config format `kit_version = 1` only; a future incompatible format requires an explicit migration rather than silently interpreting newer configuration.

## Validation boundary

Mechanical validation checks what software can know reliably: generated drift, required files, supported profiles/config format and relative Markdown links. It deliberately does not claim to validate semantic statements such as “this reverse-engineering hypothesis is established”, “this fix is generic”, or “this experiment maximizes information gain”. Those remain reviewable agent/human reasoning backed by repository evidence.
