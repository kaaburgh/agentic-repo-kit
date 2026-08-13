# Safe adoption of an existing contract

Use the `adopt` command when a repository already has hand-written files at paths that the kit would manage. Ordinary bootstrap remains appropriate for new or non-conflicting repositories.

## 1. Prepare project-owned inputs

Create the intended `.agentic-repo.toml`. Move project-specific rules that must remain project-owned into configured `[local]` policy, playbook, or PR fragments. The kit does not try to decide automatically which legacy prose is generic and which is project-specific.

## 2. Produce a non-destructive plan

```bash
agentic-repo adopt . --output /tmp/agentic-adoption.json
```

Plan mode does not create `.agentic-repo.lock.json` or replace contract files. The JSON report includes:

- the tool version and a `plan_id`;
- the config hash and configured roadmap/local-input hashes;
- every prospective managed path and its action;
- current and prospective hashes;
- a unified diff for replacements;
- operator decisions that still require review.

Review every `replace_unmanaged` diff. If required legacy policy is missing from the prospective side, preserve it in an appropriate local fragment and generate a new plan.

## 3. Transfer ownership only for the reviewed plan

```bash
agentic-repo adopt . --apply <plan-id>
agentic-repo check .
```

The plan identifier is a 64-character hexadecimal SHA-256 value over the versioned plan state. Apply rebuilds the plan and refuses a stale identifier. Changes to the tool version, config, roadmap/local inputs, existing contract files, or prospective generated output require a new review.

Apply rechecks all planned current/prospective hashes before writing. Managed files are replaced atomically and the ownership lock is written last. If a write fails after transfer starts, already-applied files are restored and newly created files are removed where possible; failure to complete rollback is reported explicitly.

After adoption, normal `check` and `upgrade` use the generated marker plus lock ownership model. A repository that already has a lock is already managed and should use `upgrade` instead of `adopt`.

## Migration review rule

Adoption makes replacement explicit; it cannot prove that deleting a paragraph from the old hand-written contract is semantically correct. The migration PR must review the replacement diffs and preserve project-specific policy in local inputs before applying the reviewed plan.
