## Reverse engineering and evidence

Prefer **observe → hypothesize → instrument → test → update model → patch**. If the cause is unknown, observability comes before a final fix. Choose experiments for information gain: one experiment that eliminates several hypotheses is better than several narrow confirmation attempts.

Keep evidence classes distinct: `static`, `runtime`, `synthetic`, `reported`, and `assumed`. A plausible symbol/function name is not a fact. Tie target-specific findings to exact target/version provenance.

Validation evidence must be independent of the transformation or mapping being validated. Do not validate a parser-derived address, mapping, decode, or identity by feeding values produced through that same derivation back into it. Prefer an independently pinned relationship, a second implementation/tool, raw-byte observation, runtime observation, or a structural invariant that can fail independently. If only internal consistency is checked, describe it as such rather than as independent validation.

Machine-readable derived RE artifacts must carry enough provenance to reject stale or semantically incompatible evidence: at minimum a schema/version identifier, identities or hashes for all material inputs that affect interpretation, and producer/tool or analysis-model identity where those can change semantics. Consumers should fail closed on missing or incompatible provenance instead of silently accepting legacy output.

Preserve ambiguity in both machine output and prose. If uniqueness is not established, emit an explicit ambiguous/unmapped result rather than selecting a convenient candidate by ordering, nearest address, fuzzy score, or other arbitrary tie-break. Heuristic relationships may rank investigation leads but remain hypotheses until stronger evidence establishes identity.

Treat ABI and calling convention as target evidence, not a compiler-default assumption. Before interpreting arguments across a closed-target call boundary or designing a hook/trampoline around it, establish the relevant register/stack behavior from real call sites, callee entry/exit behavior, known-arity calls, or equivalent direct evidence when practical.

For runtime experiments, define success with an oracle that directly distinguishes the claimed target state or behavior. Liveness, a changed frame/hash, non-empty output, or a generic timing delta proves only that something happened unless that is exactly the claim being tested. Declare termination/liveness expectations and bound waits, retries, logging, captures, and total runtime so a hung or noisy run fails closed rather than producing accidental evidence.

Keep harness capability separate from target-specific evidence. A synthetic fixture, redistributable control target, or mock can establish that input injection, breakpoint control, capture, decoding, or artifact generation works; it does not establish the corresponding behavior on the exact target until that target is run under the stated scenario and oracle.

Substantial findings belong under `docs/re/`; reproducible experiments and negative results belong under `docs/experiments/`. Save signatures, structures, call sequences, scripts, parsers, and other reusable RE outputs in the repository when licensing permits.
