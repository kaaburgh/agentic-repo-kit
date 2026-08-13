## Native binary patching

Treat addresses and offsets as version-specific until proven otherwise. Prefer public APIs/exports, stable runtime relationships, signatures with structural invariants, relative references, then exact-version offsets.

Before changing machine code or files, verify target identity and expected bytes/invariants. Require unambiguous matches and instruction boundaries; account for architecture, ABI/calling convention, stack/register preservation, RIP-relative addressing, page protection and instruction-cache flushing where relevant. Fail closed on unknown versions, zero/ambiguous matches, or unexpected bytes.

Keep DLL entry work minimal, respect loader lock, reentrancy/threading and hook lifecycle, and preserve original semantics except for the intended change. On-disk changes require backup, post-write verification, and automatic restore; prefer reversible runtime mechanisms where materially safer.
