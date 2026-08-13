## RE workflow

Start read-only where practical. Establish provenance, collect static/runtime observations, state competing hypotheses, instrument the narrowest useful seam, and update the model before patching. When the target cannot run in the current environment, continue with static analysis, parsers, fixtures, tooling, and prepared diagnostics rather than guessing runtime behavior.

### Evidence-integrity checks

Before promoting a derived result to durable evidence, ask what could make the check fail independently of the derivation itself. A parser should not validate its own address mapping by round-tripping values obtained from that mapping. Prefer one or more of:

- an independently specified header/format relationship;
- a second implementation or external generic tool that does not reuse the same derivation;
- a raw-byte/search observation with the comparison value derived separately;
- a runtime observation against the exact target;
- a structural invariant whose coverage/counts/ranges must close exactly.

A self-round-trip or same-model consistency test can still be useful, but label it as internal consistency rather than independent corroboration.

Treat serialized RE output as evidence with a compatibility boundary. Include a schema/version, identities or hashes for every material target/reference/configuration input that can affect interpretation, producer/tool version, and any parser/layout/normalization or analysis-model identifier needed to determine whether the semantics are still current. Downstream consumers should reject missing, legacy, or incompatible provenance instead of silently mixing evidence from different analysis models.

When matching or correlating candidates, make uniqueness an invariant. Zero matches, multiple equally valid matches, duplicate normalized signatures, or otherwise unresolved ties should remain explicit `unmapped`/`ambiguous` outcomes. Do not turn deterministic list order or a fuzzy best score into an identity claim. Keep heuristic alignments in human notes as investigation leads unless independently corroborated.

Before assigning argument semantics at a closed-target call boundary, recover the relevant ABI from observed behavior. Useful evidence includes a known-arity real call, caller cleanup, callee stack reads, register preparation/consumption, preserved registers, return behavior, and agreement across multiple sites. Compiler/toolchain fingerprints may guide the hypothesis but do not by themselves establish the calling convention for a specific internal boundary.
