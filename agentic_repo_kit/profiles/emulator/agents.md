## Emulator correctness

Separate guest semantics from host implementation details and from title-visible symptoms. A bug visible in one game is not automatically title-specific; first establish which emulated contract is violated and whether a generic fix is possible.

Reproducibility must identify the emulator source baseline (repository + exact commit), relevant build/configuration, guest/title build identity, host OS/CPU/GPU/driver/backend where they affect behavior, and the exact scenario.

Correctness evidence precedes performance specialization. Instrumentation must make its own overhead measurable so profiling conclusions are not artifacts of tracing.
