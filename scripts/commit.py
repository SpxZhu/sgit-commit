#!/usr/bin/env python3
"""Submit an approved Git commit in one call; retain legacy staged snapshots."""
from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import re
import sys

from git_common import (GitError, branch, commit_verified, ensure_ready,
                        git, head, index_tree, load_state, repository, run,
                        save_state, status)


KIND = "sgit-commit"
VERSION = re.compile(r"(?:0|[1-9][0-9]*)(?:\.(?:0|[1-9][0-9]*)){2}\Z")


class Parser(argparse.ArgumentParser):
    def error(self, message):
        print(json.dumps({"error": message}), file=sys.stderr)
        self.exit(2)


def version_plan(current: str, committed: str, bump: int | None = None,
                 target: str | None = None) -> dict:
    def parse(value: str) -> tuple[int, ...]:
        if not VERSION.fullmatch(value):
            raise GitError("Version must be 3 non-negative integers without leading zeros")
        return tuple(map(int, value.split(".")))

    now, old = parse(current), parse(committed)
    effective_bump = bump if bump is not None else 3
    if target is None and now < old:
        raise GitError("Current version is lower than committed version; verify authority source")
    if target is not None:
        result = parse(target)
        action = "target"
    elif bump is None and now > old:
        result, action = now, "reuse"
    else:
        parts = list(old)
        parts[effective_bump - 1] += 1
        parts[effective_bump:] = [0] * (3 - effective_bump)
        result = tuple(parts)
        if result < now:
            raise GitError("Requested version bump would overwrite a higher current version; verify and explicitly specify --target")
        action = "reuse" if result == now else "bump"
    if result <= old:
        raise GitError("Target version must be greater than committed version")
    return {"current": current, "committed": committed,
            "target": ".".join(map(str, result)), "bump": effective_bump,
            "action": action, "reuse_current": result == now}


def artifact(repo: Path, path: str | Path) -> Path:
    """Keep workflow files out of the commit and ordinary untracked output."""
    resolved = Path(path).resolve()
    try:
        relative = resolved.relative_to(repo).as_posix()
    except ValueError:
        return resolved
    if relative == ".git" or relative.startswith(".git/"):
        raise GitError("Artifacts must not be written inside .git metadata")
    tracked = run(repo, "--literal-pathspecs", "ls-files", "-z", "--", relative).stdout
    ignored = run(repo, "check-ignore", "--quiet", "--", relative, ok=(0, 1)).returncode == 0
    if tracked or not ignored:
        raise GitError("In-repo state/message/paths files must be untracked and ignored")
    return resolved


def read_message(path: Path) -> str:
    return normalize_message(path.read_text(encoding="utf-8"))


def normalize_message(message: str) -> str:
    if not isinstance(message, str):
        raise GitError("Commit message must be a string")
    if not message.strip() or message.startswith("\ufeff") or "\0" in message:
        raise GitError("Commit message must be non-empty UTF-8 text without BOM or NUL")
    return message.rstrip("\r\n") + "\n"


def selected_paths(path: Path) -> list[str]:
    return validate_paths(json.loads(path.read_text(encoding="utf-8")))


def validate_paths(values) -> list[str]:
    if not isinstance(values, list) or not values:
        raise GitError("paths-file must contain a nonempty JSON array of paths")
    result = []
    for value in values:
        if not isinstance(value, str) or not value or "\\" in value or "\0" in value:
            raise GitError("Paths must be repository-relative file paths separated by /")
        path_parts = value.split("/")
        if Path(value).drive or PurePosixPath(value).is_absolute() or any(p in ("", ".", "..") for p in path_parts):
            raise GitError("Paths must not be absolute or contain empty, ., or .. segments")
        if path_parts[0].lower() == ".git":
            raise GitError("Cannot select Git metadata")
        result.append(value)
    if len(set(result)) != len(result):
        raise GitError("Selected paths must not contain duplicates")
    return result


def staged_paths(repo: Path) -> list[str]:
    # Disabling rename detection exposes both old and new paths for range checks.
    raw = run(repo, "diff", "--cached", "--name-only", "--no-renames", "-z", "--").stdout
    return [value.decode("utf-8", "surrogateescape") for value in raw.split(b"\0") if value]


def submit(args: argparse.Namespace) -> dict:
    if not args.confirmed:
        raise GitError("Must pass --confirmed after user confirmation")
    payload = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    if not isinstance(payload, dict):
        raise GitError("stdin must be a JSON object with message, paths, and optional stage_paths")
    message = normalize_message(payload["message"])
    paths = validate_paths(payload["paths"])
    # Only explicitly selected whole files are added; mixed files keep their index.
    stage_paths = payload.get("stage_paths", [])
    if stage_paths != []:
        stage_paths = validate_paths(stage_paths)
    if set(stage_paths) - set(paths):
        raise GitError("stage_paths must be a subset of confirmed paths")
    repo = repository(args.repo)
    ensure_ready(repo)
    if "expected_head" in payload and head(repo) != payload["expected_head"]:
        raise GitError("HEAD has changed since inspection; re-verify before committing")
    outside = sorted(set(staged_paths(repo)) - set(paths))
    if outside:
        raise GitError("Index contains unconfirmed paths: " + ", ".join(outside))
    if stage_paths:
        if any((repo / path).is_dir() for path in stage_paths):
            raise GitError("stage_paths must list individual files, not directories")
        run(repo, "--literal-pathspecs", "add", "--", *stage_paths)
    # Git handles empty indexes and commit failures; hooks and signing stay enabled.
    run(repo, "commit", "--cleanup=verbatim", "-F", "-", input=message.encode("utf-8"))
    try:
        new_head, actual_message = git(repo, "log", "-1", "--format=%H%x00%B").split("\0", 1)
        remaining = status(repo)
    except (GitError, OSError, ValueError) as exc:
        raise GitError("git commit succeeded but failed to inspect output; check HEAD manually without auto-retry: " + str(exc)) from exc
    return {"phase": "committed", "commit": new_head, "message": actual_message,
            "remaining_changes": remaining}


def prepare(args: argparse.Namespace) -> dict:
    repo = repository(args.repo)
    state_path, message_path, paths_path = (artifact(repo, p) for p in
                                          (args.state, args.message, args.paths_file))
    if len({state_path, message_path, paths_path}) != 3:
        raise GitError("state, message, and paths-file must use distinct paths")
    if state_path.exists():
        raise GitError("state file already exists; use a new task file")
    ensure_ready(repo)
    paths = selected_paths(paths_path)
    snapshot_head, snapshot_branch = head(repo), branch(repo)
    snapshot_tree = index_tree(repo)
    changed = staged_paths(repo)
    if not changed:
        raise GitError("No staged changes in index; empty commit refused")
    outside = sorted(set(changed) - set(paths))
    if outside:
        raise GitError("Index contains unconfirmed paths: " + ", ".join(outside))
    if (index_tree(repo) != snapshot_tree or head(repo) != snapshot_head
            or branch(repo) != snapshot_branch):
        raise GitError("HEAD, branch, or index changed during preparation; re-prepare")
    state = {"schema": 1, "kind": KIND, "phase": "prepared", "repo": str(repo),
             "head": snapshot_head, "branch": snapshot_branch, "index_tree": snapshot_tree,
             "message_path": str(message_path), "message": read_message(message_path),
             "paths_file": str(paths_path), "paths": paths, "staged_paths": changed}
    save_state(state_path, state)
    return {"state": str(state_path), **state}


def execute(args: argparse.Namespace) -> dict:
    if not args.confirmed:
        raise GitError("Must pass --confirmed after user confirmation")
    state_path = Path(args.state).resolve()
    state = load_state(state_path, KIND)
    if state.get("phase") != "prepared":
        raise GitError("State is already executed or not prepared; cannot re-execute commit")
    repo = repository(state["repo"])
    artifact(repo, state_path)
    message_path = artifact(repo, state["message_path"])
    artifact(repo, state["paths_file"])
    ensure_ready(repo)
    if head(repo) != state["head"] or branch(repo) != state["branch"]:
        raise GitError("HEAD or branch changed since snapshot; re-prepare and confirm")
    if index_tree(repo) != state["index_tree"]:
        raise GitError("Index changed since snapshot; re-prepare and confirm")
    if read_message(message_path) != state["message"]:
        raise GitError("Commit message changed since snapshot; re-prepare and confirm")
    if not staged_paths(repo):
        raise GitError("No staged changes in index; empty commit refused")
    run(repo, "diff", "--cached", "--check")
    state["phase"] = "executing"
    save_state(state_path, state)
    try:
        result = commit_verified(repo, state["message"], state["head"], state["index_tree"])
        if branch(repo) != state["branch"]:
            raise GitError("Commit was created but branch changed; check hooks or concurrent operations")
    except Exception as exc:
        state.update(phase="failed", error=str(exc))
        save_state(state_path, state)
        raise
    state.update(phase="committed", result=result)
    save_state(state_path, state)
    return {"state": str(state_path), "phase": "committed", **result}


def main() -> int:
    parser = Parser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    version = sub.add_parser("version", help="Calculate 3-segment semver increment without touching files")
    version.add_argument("--current", required=True)
    version.add_argument("--committed", required=True)
    version.add_argument("--bump", type=int, choices=(1, 2, 3),
                         help="Explicitly bump 1=major, 2=minor, 3=patch; defaults to 3 or reuses valid ahead version")
    version.add_argument("--target")
    direct = sub.add_parser("submit", help="Read proposal from stdin JSON, stage whole files, commit and return result")
    direct.add_argument("--repo", required=True)
    direct.add_argument("--confirmed", action="store_true")
    prep = sub.add_parser("prepare", help="Capture staged snapshot for review")
    for name in ("repo", "state", "message", "paths-file"):
        prep.add_argument("--" + name, required=True)
    prep.add_argument("--staged", action="store_true", help="Submit only indexed changes")
    commit = sub.add_parser("execute", help="Verify snapshot and execute commit")
    commit.add_argument("--state", required=True)
    commit.add_argument("--confirmed", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "version":
            result = version_plan(args.current, args.committed, args.bump, args.target)
        elif args.command == "submit":
            result = submit(args)
        else:
            result = prepare(args) if args.command == "prepare" else execute(args)
        print(json.dumps(result))
        return 0
    except (GitError, OSError, ValueError, KeyError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
