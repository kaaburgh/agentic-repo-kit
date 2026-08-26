### Reverse-engineering evidence

- [ ] Established findings name evidence class and target/environment provenance.
- [ ] Validation or corroboration is independent of the derived mapping/model being validated, or is explicitly labeled internal consistency only.
- [ ] Serialized RE artifacts carry schema/input/producer provenance sufficient to reject stale or incompatible evidence.
- [ ] Ambiguous matches or correlations remain explicit; no arbitrary tie-break is promoted to identity.
- [ ] ABI/calling-convention claims used for argument interpretation or hook design are supported by observed target behavior where practical.
- [ ] Runtime experiments use a semantic success/failure oracle and explicit bounded termination contract rather than accepting generic activity as proof of the intended behavior.
- [ ] Harness/control capability evidence is not presented as target-specific runtime evidence.
- [ ] Negative results that prevent repeated dead ends are durable.
- [ ] Runtime behavior is not claimed from static or synthetic evidence alone.
- [ ] No new producer duplicates an already-tooled question whose previous result is still unrecorded.
