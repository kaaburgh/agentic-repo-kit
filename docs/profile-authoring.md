# Profile authoring

A profile is a small orthogonal policy overlay under `agentic_repo_kit/profiles/<name>/`.

Supported fragments are:

- `agents.md` — canonical rules appended to generated `AGENTS.md`;
- `playbook.md` — operational workflow appended to `docs/agent-playbook.md`;
- `pr.md` — domain-specific review checklist appended to the PR template.

Keep fragments focused on reusable domain constraints. Do not put a particular game's hashes, a repository's build commands, a one-off architecture decision, or product requirements into a built-in profile.

Before adding a new profile, ask whether the rule is:

- cross-domain and stable enough for `core`;
- domain-specific and likely to apply to multiple repositories, which justifies a profile;
- project-specific, which belongs in the target repository or `[local]` fragments.

Profile changes are behavior changes for every target repository selecting that profile. Add or update tests, run this repository's self-check, and explain upgrade impact in the PR.
