## Reverse engineering and evidence

Prefer **observe → hypothesize → instrument → test → update model → patch**. If the cause is unknown, observability comes before a final fix. Choose experiments for information gain: one experiment that eliminates several hypotheses is better than several narrow confirmation attempts.

Keep evidence classes distinct: `static`, `runtime`, `synthetic`, `reported`, and `assumed`. A plausible symbol/function name is not a fact. Tie target-specific findings to exact target/version provenance.

Substantial findings belong under `docs/re/`; reproducible experiments and negative results belong under `docs/experiments/`. Save signatures, structures, call sequences, scripts, parsers, and other reusable RE outputs in the repository when licensing permits.
