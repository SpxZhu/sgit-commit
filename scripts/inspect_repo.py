"""Collect a compact, read-only Git snapshot in one tool invocation."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import sys

from git_common import (GitError, branch, git, head, operations, repository,
                        status, worktrees)


def inspect(repo, paths=None, base=None, patch=False, include_worktrees=False):
    repo = repository(repo)
    scope = ["--", *paths] if paths else []

    def diff(*options):
        return git(repo, "--literal-pathspecs", "diff", "--no-ext-diff", "--no-textconv", *options, *scope)

    queries = {
        "head": lambda: head(repo),
        "branch": lambda: branch(repo),
        "status": lambda: status(repo),
        "operations": lambda: operations(repo),
        "staged_stat": lambda: diff("--cached", "--stat"),
        "unstaged_stat": lambda: diff("--stat"),
    }
    if base:
        # Resolve refs to a commit first; never let an input become a diff option.
        base_sha = git(repo, "rev-parse", "--verify", "--end-of-options", base + "^{commit}")
        queries["contribution_stat"] = lambda: diff("--stat", base_sha + "...HEAD")
    if patch:
        queries["staged_patch"] = lambda: diff("--cached")
        queries["unstaged_patch"] = lambda: diff()
        if base:
            queries["contribution_patch"] = lambda: diff(base_sha + "...HEAD")
    if include_worktrees:
        queries["worktrees"] = lambda: worktrees(repo)

    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {key: pool.submit(query) for key, query in queries.items()}
        result = {key: future.result() for key, future in futures.items()}

    return {
        "repo": str(repo),
        **result,
        "note": "Read-only discovery; untracked file contents and semantic review are not included. Recheck before mutation.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="Path to repository")
    parser.add_argument("--paths-file", help="UTF-8 JSON array of literal repository-relative paths")
    parser.add_argument("--base", help="Known target branch/ref for source contribution diff")
    parser.add_argument("--patch", action="store_true", help="Include complete patches for the selected paths")
    parser.add_argument("--worktrees", action="store_true", help="Include list of active worktrees")
    args = parser.parse_args()
    try:
        paths = json.loads(Path(args.paths_file).read_text(encoding="utf-8")) if args.paths_file else None
        if paths is not None and (not isinstance(paths, list) or not paths or
                                  not all(isinstance(p, str) and p for p in paths)):
            raise GitError("paths-file must contain a nonempty JSON array of paths")
        print(json.dumps(inspect(args.repo, paths, args.base, args.patch, args.worktrees), ensure_ascii=True))
    except (GitError, OSError, ValueError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=True))
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
