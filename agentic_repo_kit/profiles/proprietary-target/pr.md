### Proprietary target experiment safety

- [ ] Operator-supplied target/fixture inputs are identity-verified and left immutable; writable execution uses an isolated copy/overlay where needed.
- [ ] The detached machine-readable run record has an explicit supported schema/version and captures target/fixture, scenario/config, harness/tool, material environment, termination, semantic oracle, and artifact provenance without embedding proprietary payloads.
- [ ] Artifacts/logs are bounded and sanitize private paths, credentials, user identifiers, and unrelated host data.
- [ ] Ambiguous target or fixture selection fails closed rather than choosing a candidate silently.
