# Commit Message Guidelines

## Content Boundaries

Commit messages are derived strictly from the verified net diff. The conversation context provides intent and context, but the message itself must reflect actual code changes. First, thoroughly inspect the selected changes, then summarize the project's features, fixes, behaviors, configurations, and necessary maintenance. Combine changes across files that belong to the same logical requirement; separate independent changes into distinct bullet points. Always articulate "what was done + the necessary behavior, boundary, or purpose". Do not pad descriptions file-by-file, and do not include unfulfilled plans or unverified speculative performance claims.

Metadata such as version bumping/syncing, staging/committing/stash/worktree cleanup, test execution results, and agent status reports MUST NOT enter the commit title or body. Scope boundaries, version plans, verification status, and blockers must remain outside the committable message text block. Message filtering does not alter the confirmed commit scope; version files are still committed alongside code changes. Actual repository changes—such as new test cases or updated build configurations—must be recorded, contrasting with mere execution logs like "tests passed" or "build succeeded".

Only when the user explicitly requests a pure release bump/preparation is `chore(release): prepare release <version>` permitted, with the body detailing the actual release preparation under "Maintenance". If filtering leaves no actual project changes to describe and the commit is not an explicit release preparation, report the remaining diff and clarify user intent rather than fabricating functional changes or generating an empty message.

## Title and Categorized Body

By default, use [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) format: a standardized title and a categorized bulleted body.
Explicit repository constraints (language, type, length, or template) always take precedence over defaults.

The title format is:
`<type>(<optional scope>): <concise imperative summary>`
Do not put a period at the end of the title. The `scope` indicates an existing module; omit scope if changes span multiple modules or if there is no clear module boundary. Choose a single primary type; do not stack prefixes or split an approved commit simply because changes touch multiple categories.

| Type | Primary Purpose |
| --- | --- |
| `feat` | New feature or capability |
| `fix` | Bug fix |
| `refactor` | Code restructuring without changing external behavior |
| `perf` | Proven performance improvement |
| `docs` | Documentation changes |
| `test` | Adding or updating tests |
| `build` | Build system, packaging, or dependency updates |
| `ci` | Continuous Integration configurations |
| `style` | Formatting/whitespace changes that do not affect code semantics |
| `chore` | Routine maintenance not fitting other categories |
| `revert` | Reverting a previous commit |

The body is organized into standardized categories (only include categories that have actual content):
- Features
- Bug Fixes
- Deprecations / Removals
- Performance
- Refactoring
- Documentation
- Tests
- Build & Dependencies
- Continuous Integration
- Code Style
- Maintenance
- Reverts

*Language Note:* When operating in an English-speaking repository or context, write category headers and bullet points in English. In Chinese projects or when requested by the user, Chinese category headers and descriptions may be used.

Each category uses its own header and `- ` bullet points (do not use continuous numbering across categories). Each change belongs to only one most fitting category. When removing features, categorize under "Deprecations / Removals", while selecting the title type based on purpose (e.g., `refactor` for dead code removal, `fix` for removing erroneous behavior). Do not assume a feature was removed merely because a file was deleted.

Breaking changes must append a `!` after the type/scope in the title (e.g. `feat(api)!: change user endpoint`), and provide a footer at the very end: `BREAKING CHANGE: <explanation and migration steps>`. Other trailers are only added when explicitly requested by the user or repository conventions. Commit types do not dictate version increment levels; versions are managed per [Version Guidelines](version.md).

Previews, messages, and actual commits use the identical text: "Subject + blank line + Categorized Body + optional footer", without wrapping XML tags, markdown labels, or delivery reports. Use real newlines with a blank line separating categories.

### Example

```text
feat(level): add retry capability and improve settlement flow

Features
- Support immediate level retry after match settlement

Bug Fixes
- Fix score accumulator not resetting on retry

Deprecations / Removals
- Remove deprecated settlement screen entrypoint
```

## Discovery and Verification Checklist

Distinguish between staged, unstaged, and untracked files. New files must have their contents inspected. For binaries, lockfiles, and generated assets, verify origins and metadata rather than expanding full content unnecessarily.

Before delivering the proposal:
1. Title accurately reflects the primary intent.
2. Every category bullet point is supported by verified net diffs.
3. Breaking changes are clearly articulated.
4. Incidental metadata (agent logs, test pass markers) is kept outside the message block.
5. The proposed message matches the text that will be written.
