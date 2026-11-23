# Tags and Releases

Read this reference only when the user explicitly requests publishing. Standard commits finish locally by default and do not read this file or make network pre-checks.

Before committing, verify upstream remote/branch availability and check for local/remote tag conflicts, defaulting to `v<version>`. If the target is ambiguous, tags conflict, or publishing is known to be infeasible, resolve these blockers before committing.

After verifying the local commit, present:
- Annotated tag name (`v<version>`)
- Target commit SHA
- Upstream remote/branch
- Content to be pushed
- Release title and notes
- Release status (standard release vs. prerelease)

Obtain explicit user confirmation specifically for this publication plan.

Upon confirmation:
1. Re-verify HEAD, version, upstream, and remote tags.
2. Create an annotated tag pointing to the exact commit.
3. Push the approved branch and tag to the confirmed remote.
4. Create the Release on the hosting platform (GitHub / GitLab / Gitea) using the same tag.
5. Do not force push, move existing tags, or silently switch remotes.

Verify the remote branch and tag commit dereference, and provide the release URL. If any step fails, report which stage failed (tag / push / release), preserve the state, and check remote status before deciding recovery. Do not automatically retry operations with external side effects.
