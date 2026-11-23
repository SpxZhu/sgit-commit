# sgit-commit: Deterministic Git Commits & SemVer Pro for AI Agents

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![Conventional Commits: 1.0.0](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://www.conventionalcommits.org/en/v1.0.0/)
[![Tests: 15 Passed](https://img.shields.io/badge/Tests-15%20Passed-success.svg)](tests/)

A deterministic, token-saving Git commit and Semantic Versioning (SemVer) skill tailored for modern AI coding assistants and agents (Claude Code, Cursor, Codex, Windsurf, Antigravity, OpenClaw, Roo Code).

---

## ⚡ The Problem

When asking an AI agent to "commit my changes", standard prompting fails in predictable ways:
* **Token Exhaustion**: The agent runs 4–6 separate shell queries (`git status`, `git branch`, `git diff`, `git log`), burning thousands of context tokens on repetitive roundtrips.
* **Commit Hallucinations**: Vague, unstructured commit messages that lump unrelated files together or invent non-existent fixes.
* **Version Drift**: Version bumping (`1.2.3 → 1.2.4`) is either forgotten, decoupled from the commit, or requires multiple user corrections.
* **Destructive Overreach**: Agents attempting to force-push, wipe unstaged changes, or bypass pre-commit hooks (`--no-verify`).

---

## ✨ The Solution: How `sgit-commit` Works

`sgit-commit` couples structured agent playbooks (`SKILL.md`) with lightweight, deterministic Python standard-library scripts to execute bulletproof Git workflows:

1. **Single-Shot Multi-Threaded Inspection (`inspect_repo.py`)**:
   Captures `HEAD`, active branch, ongoing Git operations (rebase/merge/cherry-pick), full status entries, and staged/unstaged diff statistics concurrently in one instant call.
2. **Conventional Commits 1.0.0 with Categorized Breakdown**:
   Generates a standardized title (`<type>(<scope>): <summary>`) accompanied by categorized bullet points (`Features`, `Bug Fixes`, `Deprecations`, `Performance`, `Refactoring`, etc.). Adapts seamlessly between English and Chinese.
3. **Automated 3-Segment Semantic Versioning (`commit.py version`)**:
   Automatically baselines against committed `HEAD`, increments the patch segment (or specified major/minor bump), and bundles version synchronization into the same atomic commit.
4. **Atomic Submit with Strict Boundaries (`commit.py submit`)**:
   Passes the approved plan via JSON to `submit`, which verifies that no unapproved files exist in the index, stages selected files, and creates the commit while preserving GPG signatures and Git hooks.
5. **Zero External Dependencies**:
   Built strictly with Python 3.10+ standard library and the local `git` binary. No `pip install` required.

---

## 📦 Compatibility & Supported Platforms

| Platform | Location / Setup | Calling Convention |
| --- | --- | --- |
| **Agensi.io (MCP)** | Install via Agensi Marketplace | Natural language / Tool invocation |
| **Claude Code** | `~/.claude/skills/sgit-commit/` | `/sgit-commit` |
| **Cursor / Windsurf** | `~/.agents/skills/sgit-commit/` | `$sgit-commit` or prompt |
| **Codex CLI** | `~/.agents/skills/sgit-commit/` | `$sgit-commit` |
| **Antigravity** | `~/.gemini/config/skills/sgit-commit/` | `/sgit-commit` |

---

## 🚀 Quick Start & Usage

Simply invoke the skill in your agent prompt:

```text
# Standard commit: Inspect, generate message, bump version, and commit locally
/sgit-commit

# Preview only (read-only): See diff analysis, proposed message, and version plan without modifying anything
/sgit-commit preview changes only, do not commit

# Scoped commit: Only commit files related to authentication
/sgit-commit only commit files related to auth service
```

### Typical Output Preview

```text
---
Scope: src/auth.py, src/token.py, package.json
Version: 1.4.2 -> 1.4.3 (patch increment)
Proposed Commit:
feat(auth): add refresh token rotation and revoke expired sessions

Features
- Support refresh token rotation on user re-authentication
- Automatically invalidate revoked session tokens

Bug Fixes
- Fix race condition during concurrent token refresh
---
Confirm this proposal to execute commit.
```

---

## 📁 Repository Structure

```text
sgit-commit/
├── SKILL.md                 # Primary skill definition and instructions for AI agents
├── README.md                # Documentation & marketplace overview
├── LICENSE                  # MIT License
├── agents/
│   └── openai.yaml          # Agent platform interface metadata
├── references/              # Detailed specification playbooks
│   ├── commit.md            # Atomic commit execution rules & stdin schema
│   ├── message.md           # Conventional Commits format & categories
│   ├── publish.md           # Optional tagging & release workflows
│   └── version.md           # 3-segment SemVer increment rules
├── scripts/                 # Self-contained Python standard-library scripts
│   ├── __init__.py
│   ├── commit.py            # Atomic submit & SemVer calculator
│   ├── git_common.py        # Shared Git primitives & worktree handlers
│   └── inspect_repo.py      # Single-shot multithreaded repository inspection
└── tests/                   # Automated unit and integration test suite
    ├── test_commit.py       # Full commit lifecycle & version tests
    └── test_inspect.py      # Repository inspection & snapshot tests
```

---

## 🧪 Testing

Run the included test suite against any local Python 3.10+ installation:

```bash
python -m unittest discover -s tests -v
```

All tests execute in isolated, disposable temporary Git repositories without altering your local development environment.

---

## 🔒 Security & Privacy

* **100% Local Execution**: Operates purely within your local file system and Git binary.
* **No Telemetry / No Network Calls**: Never sends code, diffs, or metadata to any external server.
* **Human-in-the-Loop Confirmation**: Modifying files or creating commits strictly requires user confirmation.

---

## 📄 License

Distributed under the [MIT License](LICENSE). Copyright (c) 2026 SpxZhu.
