## Blind-research workflow

Before target-specific investigation starts, read the project-local blind-research gate definition: what evidence is in-boundary, what repository state is supported, and what durable condition ends the blind phase. If those project-specific boundaries are not defined, do not invent them from this generic profile; record that the provenance experiment itself is underspecified before claiming `clean` blind results.

During the active gate:

- search the target and project-generated evidence before searching for target-specific recovered answers;
- general format/compiler/ABI/debugger/tool documentation is valid research input, but target-specific recovered internals are not a shortcut;
- keep `clean` / `contaminated` / `external-assisted` provenance separate from the normal evidence class;
- when parallel work could expose target-specific answers, avoid reading the other work until the independent finding is durably preserved when practical;
- if accidental disclosure occurs, stop reading the source, record the exposure boundary and timing, identify which conclusions could have been influenced, and independently re-establish facts from allowed evidence where useful for correctness without relabeling them `clean`;
- do not use unsupported repository history as a hidden external-knowledge channel.

A pre-unlock rescue is exceptional, not a faster research mode. The experiment record should say what was attempted, what remains blocked, why the external source class is needed, and what narrower alternatives failed. The maintainer's durable unlock should identify only the bounded question/source class needed to proceed. Downstream findings that depend on the rescue remain `external-assisted`.

After the blind gate ends, preserve the independent result before external comparison. The separate verification result reports agreements, disagreements, missed structures, and false positives so outside knowledge does not rewrite the historical blind-research record.

For operator-provided tools or artifacts, separate generic capability from recovered target knowledge. A generic debugger/disassembler/compiler tool may be accepted under normal project rules; an artifact containing target-specific recovered addresses, symbols, structures, pseudocode, or semantic maps follows the same contamination/rescue policy as any other external recovered source.
