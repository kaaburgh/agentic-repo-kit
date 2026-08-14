# Executable distribution contract

`agentic-repo-kit` separates repository policy from the executable tool used to maintain that policy. Generated `AGENTS.md` and related docs are self-contained for agents, while deterministic commands such as `check`, `upgrade`, and `adopt` run versioned kit code.

## Consumer source of truth

Lock format 2 records the exact executable distribution identity:

```json
{
  "format": 2,
  "tool_version": "0.1.9",
  "distribution": {
    "repository": "kaaburgh/agentic-repo-kit",
    "release": "v0.1.9",
    "artifact": "agentic-repo-kit-0.1.9.pyz",
    "sha256": "...",
    "tool_version": "0.1.9"
  }
}
```

For normal validation, the consumer repository trusts these committed coordinates and digest. It must not silently substitute `latest`, another tag, another artifact name, or a checksum downloaded alongside an untrusted artifact.

`bootstrap`, `adopt`, and `upgrade` write the distribution identity atomically as part of the generated lock. A tool-version upgrade therefore updates generated policy provenance and executable coordinates in one reviewable repository change.

## Preferred executable artifact

Each tool release publishes `agentic-repo-kit-<version>.pyz`. The zipapp is dependency-free apart from Python 3.11+ and is the canonical executable artifact for consumers:

```bash
python agentic-repo-kit-0.1.9.pyz check /work/repository
python agentic-repo-kit-0.1.9.pyz upgrade /work/repository
```

The `.pyz` is deterministic. Its release digest is committed in `agentic_repo_kit/distribution.json`; that metadata file is deliberately excluded from the zipapp so the digest does not recursively change the artifact it describes. When running from a source/wheel install the renderer reads the committed metadata. When running inside the zipapp it hashes its own archive and writes that same identity into target locks.

The release workflow rebuilds the zipapp from the release commit and refuses publication if its SHA-256 differs from the digest committed in the dogfood lock.

## Managed contract check workflow

Kit-managed repositories receive `.github/workflows/agentic-repo-check.yml` as generated output. The workflow is intentionally limited to repository-contract validation rather than project build/test policy.

On every pull request and push it:

1. reads only the committed format-2 lock;
2. validates the pinned distribution repository, release, artifact name, tool version, and SHA-256;
3. downloads the exact public `.pyz` from the named GitHub Release without a cross-repository secret;
4. verifies the downloaded bytes against `distribution.sha256` from the lock;
5. runs `python <artifact>.pyz check .`.

The workflow uses broad triggers rather than path filters because the generated contract and its validation inputs span policy, configuration, local fragments, roadmap, and generated files. It has only `contents: read` permission and does not read repository secrets.

The workflow itself is a trusted generated path and participates in the generated manifest. `check` reports edits to it as drift, and `upgrade` may update an already managed copy. If a repository already has an unmarked, project-owned workflow at the same path, upgrade fails closed rather than replacing it silently.

### Pre-release self-hosting in agentic-repo-kit

The kit repository has one bootstrap-cycle exception. A version-bump PR necessarily pins a `.pyz` that is not public until that PR merges and the release workflow runs. If—and only if—the lock's distribution repository is the current GitHub repository and the public download is unavailable, the managed check workflow may build the deterministic `.pyz` from the checked-out source with `scripts/build_pyz.py`. The result must still match the SHA-256 already committed in the lock before it can execute `check`.

Ordinary consumer repositories do not receive this fallback in practice because their `GITHUB_REPOSITORY` differs from the distribution repository. A failed public artifact download therefore fails closed for consumers.

## Online acquisition

Because the repository and releases are public, a consumer can download the exact artifact named by its lock without a cross-repository secret. After download, compute SHA-256 locally and compare it with `distribution.sha256` from the consumer lock before executing the artifact.

`SHA256SUMS` is also published with each GitHub Release. It is useful for release-level provenance and independent cross-checks, but it is not the consumer's trust anchor: the expected artifact digest is already committed in the consumer repository's lock.

## Offline/operator handoff

If the environment has no usable network path, the operator supplies only the exact `.pyz` artifact named in the lock. The agent computes its SHA-256 and compares it with the lock before execution. A separately supplied checksum file is optional because accepting both an artifact and its checksum from the same handoff would not add an independent trust anchor.

If the artifact does not match the lock, fail closed and request the correct versioned artifact. Do not regenerate or edit the expected digest locally to make an unverified artifact pass.

## Source archives

Releases continue to publish deterministic `.tar.gz` and `.zip` source archives plus `SHA256SUMS`. They remain useful for inspection, development, and environments that intentionally run from an extracted checkout. Consumer automation should prefer the pinned `.pyz` unless it specifically requires source form.
