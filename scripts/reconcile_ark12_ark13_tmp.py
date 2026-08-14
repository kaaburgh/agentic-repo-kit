from pathlib import Path
import re

path = Path('ROADMAP.md')
text = path.read_text(encoding='utf-8')

ark12 = '''### ARK12 — Publish a pinned executable distribution contract

- **Status:** Completed and verified
- **Priority:** High
- **Category:** Distribution / constrained environments
- **Depends on:** ARK11
- **Problem / question:** Can every consumer repository pin one directly executable, reproducible kit artifact—including its acquisition coordinates and SHA-256—in the lock so online CI and offline operator handoff use the same trust anchor without vendoring the dependency?
- **Known evidence:** BB upgrade to v0.1.7 exposed that source archives solve package-registry independence but consumer repositories still need prose to discover/acquire the checker. Making the kit repository public removed the cross-repository credential requirement while preserving the need for an immutable executable distribution identity.
- **Implementation evidence:** ARK12 adds deterministic `agentic-repo-kit-<version>.pyz` builds, source/wheel distribution metadata, self-hashing identity when executing inside the zipapp, and lock format 2 with `repository`/`release`/`artifact`/`sha256`/`tool_version`. The committed digest metadata is deliberately excluded from the zipapp to avoid cryptographic self-reference. Release publication rebuilds the artifact and fails closed unless its SHA-256 equals the lock digest. Tool/package version is 0.1.8 while config `kit_version = 1` remains unchanged.
- **Validation evidence:** Draft PR #12 used CI as the deterministic builder: all non-placeholder tests passed and produced SHA-256 `7e44e7eb9b81dc3ca357ab98a4f6170bf900bea9673ea27ec831768e7acf5847`; final-head CI #66 passed after the digest was pinned. PR #12 rebase-merged at `f95068f36c839cc2df21cea3067674b3f7679c9a`. Post-merge release testing found two real recovery defects before publication (nested-shell parsing and an invalid history-derived release target); bounded follow-up PRs #13–#15 corrected release recovery to preserve exact version-owning commit identity. Release run #6 then published `v0.1.8` at exact ARK12 commit `f95068f36c839cc2df21cea3067674b3f7679c9a` with `.pyz`, tar/zip, and `SHA256SUMS`; the published `.pyz` digest exactly matches the lock. After the one-time recovery fallback was removed, Release run #7 passed the verification-only existing-tag/digest path with build/create/repair correctly skipped.
- **Validation / acceptance:**
  - deterministic `.pyz` builds are byte-identical across repeated builds from the same source tree;
  - the executable runs normal CLI commands with Python 3.11+ and no package-registry dependency;
  - lock format 2 records exact public repository/release/artifact coordinates and SHA-256 together with tool/config/profile/generated provenance;
  - `bootstrap`, `adopt`, and `upgrade` atomically emit those distribution coordinates as part of the lock;
  - source/wheel mode and zipapp mode render the same distribution identity without embedding the digest metadata into the artifact it describes;
  - the release workflow refuses publication if a rebuilt `.pyz` digest differs from the committed lock digest and verifies/repairs existing assets against that digest;
  - normal version publication preserves the exact version-owning push SHA; explicit recovery requires an exact ancestor `target_sha` rather than guessing from history;
  - offline handoff needs only the artifact because the expected digest is already committed in the consumer lock;
  - `SHA256SUMS` remains a release-level cross-check, not the consumer trust anchor;
  - package/tool version advanced to 0.1.8, lock format advanced to 2, and config `kit_version = 1` remained stable.
- **Artifacts / docs:** `scripts/build_pyz.py`, `agentic_repo_kit/distribution.py`, `agentic_repo_kit/distribution.json`, renderer/lock format 2, release workflow, `docs/distribution.md`, focused tests, GitHub Release `v0.1.8`
- **Estimated scope:** Medium

'''

ark13 = '''### ARK13 — Generate the repository contract check workflow

- **Status:** Completed and verified
- **Priority:** High
- **Category:** Core tooling / managed CI
- **Depends on:** ARK12
- **Problem / question:** Can the kit make its own deterministic contract validation a managed target-repository invariant rather than requiring every consumer to hand-author a GitHub Actions workflow?
- **Known evidence:** BB had a valid repo-kit contract but no generic contract-check Actions workflow. ARK12 supplied a public pinned executable plus digest in lock format 2, making a secret-free consumer workflow possible.
- **Implementation evidence:** ARK13 generates and owns `.github/workflows/agentic-repo-check.yml`. The workflow has `contents: read` only, broad pull-request/push triggers with no path filters, validates all lock distribution fields, downloads the exact public `.pyz`, verifies SHA-256 against `distribution.sha256`, and runs `python <artifact>.pyz check .`. It uses current `actions/checkout@v7` and `actions/setup-python@v7`. The workflow itself is a trusted generated path; `check` detects drift and `upgrade` adds/updates a managed copy while refusing an unmarked project-owned conflict. The kit repository alone may deterministically self-build the not-yet-published `.pyz` during a version-bump PR when its lock distribution repository equals `GITHUB_REPOSITORY`; that artifact must still match the committed digest before execution. Tool/package version is 0.1.9 with lock format 2 and config `kit_version = 1` unchanged.
- **Validation evidence:** Before `v0.1.9` existed, the generated workflow exercised the pre-release self-host path and produced final deterministic SHA-256 `79e914bc322873025f41db0ffa118bd037362b77708e4433bb854d8dd42b041e`; managed workflow run #29 then passed Resolve → Acquire → Verify → `check` end-to-end with that digest. Final ARK13 head passed ordinary CI #89 and managed contract workflow #35. PR #16 rebase-merged as `5a2bb177927c0a7ad465cdd2569f93f305a9e896`; post-merge managed check passed and Release #8 published `v0.1.9` at that exact commit with `.pyz` digest `79e914bc322873025f41db0ffa118bd037362b77708e4433bb854d8dd42b041e`. BB dogfood PR #12 then upgraded a real pre-ARK13 repository from lock format 1/tool 0.1.7 to format 2/tool 0.1.9 with exactly two managed changes: the lock and new workflow. BB Agentic repository contract run #3 downloaded the public 44,098-byte v0.1.9 `.pyz` from GitHub (self-host fallback was ineligible), verified the lock digest, and printed `agentic repository contract is consistent`; the independent Bloodborne target-manifest run also passed. BB PR #12 rebase-merged as `51ed6cd235d0ef9223d6e9811b283fe8a02faf7c`. Project-owned BB acquisition guidance was then reconciled through the published v0.1.9 `upgrade`/`check` path and merged in BB PR #13 as `ae52ef93710e03208ab9f223416820c53770d1cf`.
- **Validation / acceptance:**
  - generated workflow uses only coordinates/digest from the committed lock and never resolves a release via `latest`;
  - public acquisition requires no cross-repository secret;
  - SHA-256 is checked against `distribution.sha256` before execution;
  - the workflow runs `python <artifact>.pyz check .` and fails on contract/roadmap drift;
  - the workflow is a trusted generated path, participates in ownership/drift checking, and upgrades transactionally with other managed outputs;
  - a project-owned same-name workflow is not silently overwritten;
  - self-host acquisition is restricted to the distribution repository's own pre-release bootstrap cycle and still requires the lock digest;
  - focused tests cover rendered semantics, drift, upgrade from pre-ARK13 state, and unmanaged-path refusal;
  - BB dogfood receives the workflow through ordinary upgrade and proves the public download/verify/check consumer path in real GitHub Actions;
  - package/tool version advanced to 0.1.9 while config `kit_version = 1` remained stable.
- **Artifacts / docs:** workflow template, generated dogfood workflow, renderer/ownership allowlist, `tests/test_managed_check_workflow.py`, `docs/distribution.md`, package version, GitHub Release `v0.1.9`, BB PRs #12/#13
- **Estimated scope:** Medium

'''

text, count12 = re.subn(r'### ARK12 —.*?(?=### ARK13 —)', ark12, text, flags=re.S)
if count12 != 1:
    raise SystemExit(f'expected one ARK12 block, got {count12}')
text, count13 = re.subn(r'### ARK13 —.*?(?=## Later)', ark13, text, flags=re.S)
if count13 != 1:
    raise SystemExit(f'expected one ARK13 block, got {count13}')
path.write_text(text, encoding='utf-8')
