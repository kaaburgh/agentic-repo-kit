## Unattended agent cycles

When `unattended-agent-cycle` is selected, every unattended scheduled run must read and follow [`docs/agent-cycle-run.md`](./docs/agent-cycle-run.md) before selecting work, writing commits, requesting review, or reporting a verdict. Treat the committed cycle contract as immutable for the duration of that run; changes to the contract are ordinary roadmap work reviewed in a separate cycle.
