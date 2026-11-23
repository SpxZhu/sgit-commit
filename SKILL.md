---
name: sgit-commit
description: Inspect repository diffs with minimal token overhead, generate Conventional Commits with structured categorization and automated 3-segment SemVer bumping, and perform atomic local commits upon explicit user confirmation.
---

# Git Commit (sgit-commit)

Execute within the current session without restarting workflow contexts or spawning redundant sub-agents. Read repository-specific guidelines if present. Uses Python 3.10+ standard library and the local Git binary; zero external dependencies required.

## 1. Read-Only Discovery & Preview

1. **Single-Shot Repository Inspection**:
   Run `scripts/inspect_repo.py` once:
   ```bash
   python scripts/inspect_repo.py --repo <path-to-repo>
   ```
   This returns `HEAD`, branch, active Git operations, all file status entries, and both staged and unstaged diff stat summaries in a single call with parallel execution. Do not rerun repetitive individual `git status` or `git branch` queries.

2. **Scope Selection**:
   By default, select only changes relevant to the current session or task. For staged-only requests, rely strictly on the index. Read selected diffs using `git --literal-pathspecs diff -- <paths...>` / `diff --cached`. For large changesets, inspect on a per-file basis. When multiple unrelated changes are present in the worktree, isolate and verify the relevant files with the user.

3. **Message Formulation**:
   Follow [Commit Message Guidelines](references/message.md) to generate a single Conventional Commits subject and categorized body (Features, Bug Fixes, Deprecations, Refactoring, Docs, Tests, Build, CI, Style, Chore, Reverts). Adapt the body language to the repository or user preference (English by default, Chinese when working in Chinese). Do not invent changes when there is no net diff.

4. **Preview Delivery**:
   If the user only requests a preview or draft, present the candidate file scope, version increment plan, and formatted commit message in a copyable text block, then finish. When the user requests a commit, read [Commit Execution](references/commit.md) before presenting the confirmation proposal.

## 2. Three-Segment Semantic Versioning

Follow [Version Guidelines](references/version.md). Baseline against the committed version at current `HEAD`.
By default, automatically increment the third segment (patch: `1.2.3 → 1.2.4`) using `scripts/commit.py version`:
```bash
python scripts/commit.py version --current <current_val> --committed <committed_val>
```
If the working copy already contains an approved version upgrade higher than the baseline, reuse it. Routine patch increments are confirmed as part of the unified commit proposal.

## 3. Confirmation & Atomic Execution

Before committing, present a complete proposal to the user:
- **Files to commit**: Explicit paths and staging mode
- **Version plan**: Source file, baseline value, candidate value, and target value
- **Commit message**: Full subject and categorized body

Obtain explicit confirmation for this specific proposal. Vague statements like "commit directly" do not bypass confirmation.

Upon user confirmation, update version files, stage approved files, and execute atomic submission in one step via standard input:
```bash
python scripts/commit.py submit --repo <repo> --confirmed
```
Input payload format:
```json
{
  "message": "<Subject + Categorized Body>",
  "paths": ["<approved_file_1>", "<version_file>"],
  "stage_paths": ["<approved_file_1>", "<version_file>"],
  "expected_head": "<HEAD_SHA_from_initial_inspect>"
}
```

The `submit` command verifies that the Git index contains no out-of-scope files, stages specified files, invokes `git commit` (preserving user signature and hooks), and returns the new commit SHA and status.

## 4. Optional Tag & Release

Standard commits finish locally. Only when the user explicitly requests a release or push, read [Tags and Releases](references/publish.md), and separately confirm the tag name (`v<version>`), target remote, push branch, and release notes before executing.

## 5. Security & Trust Principles

- **Local Execution**: All scripts operate locally using the Python standard library and standard Git CLI. No external network requests, analytics, or telemetry are made.
- **Safety First**: Never runs force pushes, destructive resets, or hook bypasses (`--no-verify`).
- **Human-in-the-Loop**: Strict confirmation boundary before modifying repository state or committing code.
