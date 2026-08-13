## Upstream-first changes

When the project sits on an upstream codebase, first ask whether the observed behavior is a generic semantic/correctness issue. Prefer a minimal generic fix or diagnostic that can be reviewed upstream over a title-specific workaround when evidence supports it.

Keep target-specific reproduction and upstream-generic reasoning separable. Where practical, add synthetic/unit regression coverage independent of proprietary content. If a guarded specialization is necessary, document why the generic path cannot safely express the optimization or fix.
