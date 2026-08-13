## Source of truth and scope

When sources disagree, prefer: the current task and explicit maintainer decisions; current reproducible evidence; current source/tests/tool output; the live roadmap; durable project documentation; then historical notes. Do not implement an old plan merely because it exists.

`ROADMAP.md` is live project state. A PR must update its selected item when the PR changes status, evidence, dependencies, sequencing, compatibility, direction, or acceptance criteria. Preserve negative results and disproved premises instead of silently deleting the reasoning.

Keep work bounded. Do not opportunistically absorb adjacent roadmap items unless inseparable. A PR must be understandable without chat history.

## Validation and claims

Run the narrowest meaningful checks first, then broader checks warranted by the change. State exactly what ran and what did not. Compilation, linting, or synthetic tests do not establish real-target behavior.

Do not invent commands, targets, performance numbers, supported versions, or architecture details. If an important premise is unknown, turn it into an observation or experiment before implementation.
