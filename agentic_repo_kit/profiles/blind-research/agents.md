## Blind research provenance

This profile is opt-in for projects that deliberately want to measure or preserve independent discovery before consulting pre-existing target-specific recovered knowledge. It is a research provenance constraint, not a default rule for all reverse engineering.

While the project's blind-research gate is active, recover target internals from the project's allowed primary evidence: supplied or reproducibly acquired target bytes, project-generated static/runtime observations and derived artifacts, current supported repository state, general technology/tool documentation, and user-facing/official behavior documentation that does not disclose recovered internals. The project must define the gate boundary and the event or decision that ends it in durable local policy or roadmap state; this profile does not invent a milestone name for that project.

Before the gate is unlocked, do not intentionally use target-specific recovered material that substantially substitutes for independent discovery, including external decompilations/disassemblies, symbol/address/patch maps, reconstructed structs/types/layouts, target-specific analysis databases, cheat/address tables, source ports or reconstructed source that expose internals, or third-party implementation details that reveal the target seam being investigated. General tooling research remains allowed.

For blind-research accounting, treat the supported repository state as the current mainline tree plus the branch/PR under review unless project-local policy explicitly defines a different durable boundary. Do not mine abandoned/closed PRs, deleted material, old branches, or unsupported history for target-specific answers while the gate is active. Preserving old negative results for normal engineering and excluding unsupported historical target knowledge from a blind experiment are separate concerns; if a useful historical result is encountered accidentally, re-establish it from allowed evidence where practical before using it as supported project evidence.

Blind-research provenance is a separate dimension from evidence class. Use `clean`, `contaminated`, and `external-assisted` (or an explicitly project-defined equivalent vocabulary) without replacing `static`, `runtime`, `synthetic`, `reported`, or `assumed`. `clean` means no known prohibited target-specific disclosure or rescue influenced the finding. `contaminated` means accidental disclosure may have suggested the answer, search path, or confirmation threshold. `external-assisted` means a documented pre-unlock rescue source materially contributed to the finding.

If prohibited target-specific recovered knowledge is encountered accidentally, stop inspecting that source, do not copy its recovered details into the project, disclose the event, and mark conclusions that may have been influenced as `contaminated`. Independently re-establishing the same fact can validate correctness but does not restore blindness or remove the contamination modifier for experiment accounting.

External target-specific research has two supported paths while this profile is active:

1. **Post-blind verification.** Preserve the independent result first; after the project-defined blind gate ends, external material may be used for a separately identified comparison/corroboration phase.
2. **Bounded rescue before unlock.** First record a concrete blocker or negative result in durable experiment/project state. Then require an explicit maintainer decision recorded durably in the relevant roadmap/policy state, naming the bounded question and allowed source class and stating that the exception does not generalize. Findings depending on that source remain `external-assisted` and do not count as independent blind-research success.

An ordinary task/chat instruction, convenience argument, or agent decision does not silently waive an active blind-research boundary. A pre-unlock exception must use the project's recorded rescue path.
