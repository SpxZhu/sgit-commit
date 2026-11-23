# Version Guidelines

When creating a commit, `sgit-commit` defaults to incrementing the patch segment of a 3-segment semantic version (e.g., `1.2.3 → 1.2.4`). In preview-only mode, it calculates and displays the version plan without modifying files. Always verify that actual project changes exist or that the user has explicitly requested a pure version bump; do not bump versions merely to fabricate a commit.

## Determining the Version Plan

Locate the authoritative version and synchronized locations from known repository entrypoints; do not blindly scan entire repositories guessing version locations.
- Standard commits baseline against the committed version at current `HEAD`.
- If the current working copy already has a version higher than baseline, reuse it rather than bumping repeatedly.

Use `scripts/commit.py version` to calculate:
`--current` is the current candidate version, and `--committed` is the baseline commit version. By default, the 3rd segment (patch) is incremented by 1.

```text
python scripts/commit.py version --current 1.2.3 --committed 1.2.3
python scripts/commit.py version --current 1.2.4 --committed 1.2.3
```

Only use `--bump 1` (major) or `--bump 2` (minor), or specify `--target <version>` when the user or repository explicitly requests it. Never automatically infer major/minor bumps solely from `feat`, `fix`, or `!` prefixes. Routine patch increments are included directly in the proposed plan without asking redundant questions.

If version sources are missing, non-3-segment, conflicting, or mixed with out-of-scope edits, present the issue and proposal clearly for confirmation. When there is no prior committed version in an initial repo, confirm the initial 3-segment version without inventing a `--committed` value.

## Writing and Verification

The proposal presented to the user displays:
- Version source location
- Baseline version
- Candidate version
- Target version
- Files to be updated

Version calculation scripts do not edit files directly. The agent updates the authoritative version and convention sync locations, staging only approved contents.

Verify actual net diffs before modifying version files. If all changes are already absorbed and no net diff remains, skip version bumping and commit creation. Otherwise, update and stage the version files according to the confirmed plan, then execute atomic commit submission.
