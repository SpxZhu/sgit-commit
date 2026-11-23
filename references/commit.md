# Commit Execution

Read this reference before presenting the confirmation proposal whenever a commit is to be performed. All scope, version sources, messages, and existing verification must be fully prepared beforehand. By default, commits are strictly local and do not perform network calls or release pre-checks.

## Execution After User Confirmation

Update version files per the approved plan and verify written values. Execute version file staging and commit submission in a single continuous tool step.
Pass entire confirmed paths to the script for atomic staging; for mixed files containing unapproved hunks, pre-stage only approved hunks manually. "Staged-only" mode preserves the existing index and only appends approved version updates. Renames must include both old and new paths in the scope.

Pass the following JSON payload via standard input (UTF-8, real newlines; do not concatenate messages into shell strings):

```json
{
  "message": "fix(level): fix score calculation after retry\n\nBug Fixes\n- Reset score accumulator when retrying level\n",
  "paths": ["src/level.lua", "version.txt"],
  "stage_paths": ["src/level.lua", "version.txt"],
  "expected_head": "<HEAD SHA returned from pre-confirmation inspect>"
}
```

- `paths`: Array of all approved files.
- `stage_paths`: Subset of files to be whole-file staged automatically by the script (default empty array). Exclude mixed files or files from staged-only mode from `stage_paths`.
- Paths must be relative to repository root and separated by `/`. Use `null` for `expected_head` in initial commits.

Invoke the script:

```text
python scripts/commit.py submit --repo <repo> --confirmed
```

`submit` performs a single atomic pre-check:
1. Rejects any out-of-scope files present in the Git index.
2. Stages files listed in `stage_paths`.
3. Invokes `git commit` directly, preserving author identity, GPG signatures, and repository pre-commit hooks.
4. Returns the commit SHA, actual message, and remaining status.

Upon normal success, report the result immediately. Do not redundantly re-run inspection, diffs, or tree verifications.

Only execute pre-commit checks explicitly required by the repository and lacking applicable evidence. Pure commit execution does not trigger full builds, tests, or code reviews.

If commit fails, preserve the working tree and inspect error outputs and the actual `HEAD` before deciding on recovery; do not auto-retry, amend, reset, or bypass hooks. If the user explicitly requests publishing, proceed to [Publish Guidelines](publish.md).
