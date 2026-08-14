# Executable distribution contract

`agentic-repo-kit` separates repository policy from the executable tool used to maintain that policy. Generated `AGENTS.md` and related docs are self-contained for agents, while deterministic commands such as `check`, `upgrade`, and `adopt` run versioned kit code.

## Consumer source of truth

Lock format 2 records the exact executable distribution identity:

```json
{
  "format": 2,
  "tool_version": "0.1.8",
  "distribution": {
    "repository": "kaaburgh/agentic-repo-kit",
    "release": "v0.1.8",
    "artifact": "agentic-repo-kit-0.1.8.pyz",
    "sha256": "...",
    "tool_version": "0.1.8"
  }
}
```

For normal validation, the consumer repository trusts these committed coordinates and digest. It must not silently substitute `latest`, another tag, another artifact name, or a checksum downloaded alongside an untrusted artifact.

`bootstrap`, `adopt`, and `upgrade` write the distribution identity atomically as part of the generated lock. A tool-version upgrade therefore updates generated policy provenance and executable coordinates in one reviewable repository change.

## Preferred executable artifact

Each tool release publishes `agentic-repo-kit-<version>.pyz`. The zipapp is dependency-free apart from Python 3.11+ and is the canonical executable artifact for consumers:

```bash
python agentic-repo-kit-0.1.8.pyz check /work/repository
python agentic-repo-kit-0.1.8.pyz upgrade /work/repository
```

The `.pyz` is deterministic. Its release digest is committed in `agentic_repo_kit/distribution.json`; that metadata file is deliberately excluded from the zipapp so the digest does not recursively change the artifact it describes. When running from a source/wheel install the renderer reads the committed metadata. When running inside the zipapp it hashes its own archive and writes that same identity into target locks.

The release workflow rebuilds the zipapp from the release commit and refuses publication if its SHA-256 differs from the digest committed in the dogfood lock.

## Online acquisition

Because the repository and releases are public, a consumer can download the exact artifact named by its lock without a cross-repository secret. After download, compute SHA-256 locally and compare it with `distribution.sha256` from the consumer lock before executing the artifact.

`SHA256SUMS` is also published with each GitHub Release. It is useful for release-level provenance and independent cross-checks, but it is not the consumer's trust anchor: the expected artifact digest is already committed in the consumer repository's lock.

## Offline/operator handoff

If the environment has no usable network path, the operator supplies only the exact `.pyz` artifact named in the lock. The agent computes its SHA-256 and compares it with the lock before execution. A separately supplied checksum file is optional because accepting both an artifact and its checksum from the same handoff would not add an independent trust anchor.

If the artifact does not match the lock, fail closed and request the correct versioned artifact. Do not regenerate or edit the expected digest locally to make an unverified artifact pass.

## Source archives

Releases continue to publish deterministic `.tar.gz` and `.zip` source archives plus `SHA256SUMS`. They remain useful for inspection, development, and environments that intentionally run from an extracted checkout. Consumer automation should prefer the pinned `.pyz` unless it specifically requires source form.
