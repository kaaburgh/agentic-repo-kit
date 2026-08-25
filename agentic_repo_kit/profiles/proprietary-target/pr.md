### Proprietary target experiment safety

- [ ] Operator-supplied target/fixture inputs are identity-verified and left immutable; writable execution uses an isolated copy/overlay where needed.
- [ ] The detached machine-readable run record has an explicit supported schema/version and captures target/fixture, scenario/config, harness/tool, material environment, termination, semantic oracle, and artifact provenance without embedding proprietary payloads.
- [ ] Artifacts/logs are bounded and sanitize private paths, credentials, user identifiers, and unrelated host data.
- [ ] Ambiguous target or fixture selection fails closed rather than choosing a candidate silently.
- [ ] Gated items state `Operator cost` as `<sessions> × <minutes>` or `unknown (measured by <ID>)`; no estimate was invented to replace an unknown.
- [ ] A first successful gated run recorded measured end-to-end operator time in its run record and durable docs.
- [ ] A batched session established matching baselines, scenario/config identity, instrumentation build and run provenance, named every item it serves, and did not merge their acceptance.
