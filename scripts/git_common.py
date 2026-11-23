"""Small Git primitives shared by sgit workflows (Python standard library)."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import tempfile


class GitError(RuntimeError):
    pass


def run(repo, *args, input=None, ok=(0,)):
    env = os.environ.copy()
    env["GIT_OPTIONAL_LOCKS"] = "0"
    result = subprocess.run(
        ["git", "--no-pager", "-C", str(repo), *map(str, args)],
        input=input, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env,
    )
    if result.returncode not in ok:
        detail = (result.stderr or result.stdout).decode("utf-8", errors="replace").strip()
        raise GitError(f"git {args[0]} failed ({result.returncode}): {detail}")
    return result


def git(repo, *args, input=None, ok=(0,)):
    return run(repo, *args, input=input, ok=ok).stdout.decode(
        "utf-8", errors="surrogateescape"
    ).rstrip("\r\n")


def repository(path):
    return Path(git(path, "rev-parse", "--show-toplevel")).resolve()


def head(repo):
    result = run(repo, "rev-parse", "--verify", "HEAD", ok=(0, 128))
    return result.stdout.decode("ascii").strip() if result.returncode == 0 else None


def branch(repo):
    result = run(repo, "symbolic-ref", "--quiet", "--short", "HEAD", ok=(0, 1))
    return result.stdout.decode("utf-8", errors="surrogateescape").strip() or None


def status(repo):
    records = run(repo, "status", "--porcelain=v1", "-z", "--untracked-files=all").stdout.split(b"\0")
    entries = []
    cursor = 0
    while cursor < len(records) and records[cursor]:
        record = records[cursor]
        entry = {"x": chr(record[0]), "y": chr(record[1]),
                 "path": os.fsdecode(record[3:])}
        if "R" in entry["x"] + entry["y"] or "C" in entry["x"] + entry["y"]:
            cursor += 1
            entry["original"] = os.fsdecode(records[cursor])
        entries.append(entry)
        cursor += 1
    return entries


def operations(repo):
    directory = Path(git(repo, "rev-parse", "--absolute-git-dir"))
    return [name for name in ("MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD",
                             "rebase-merge", "rebase-apply", "sequencer",
                             "BISECT_LOG", "index.lock")
            if (directory / name).exists()]


def ensure_ready(repo):
    overrides = [key for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE")
                 if os.environ.get(key)]
    if overrides:
        raise GitError("Explicit Git environment overrides require manual review: " + ", ".join(overrides))
    active = operations(repo)
    if active:
        raise GitError("Git operation in progress: " + ", ".join(active))
    if run(repo, "ls-files", "-u", "-z").stdout:
        raise GitError("Unresolved index entries; resolve and review before continuing")
    entries = run(repo, "ls-files", "-v", "-z").stdout.split(b"\0")
    if any(entry and (entry[:1] == b"S" or entry[:1].islower()) for entry in entries):
        raise GitError("skip-worktree / assume-unchanged index entries require manual review")


def index_tree(repo):
    return git(repo, "write-tree")


def load_state(path, kind):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema") != 1 or data.get("kind") != kind:
        raise GitError("State schema or workflow does not match")
    return data


def save_state(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                                         dir=path.parent, prefix=".sgit-", delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(data, stream, ensure_ascii=True, indent=2)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def commit_verified(repo, message, expected_head, expected_tree):
    ensure_ready(repo)
    if head(repo) != expected_head or index_tree(repo) != expected_tree:
        raise GitError("HEAD or index changed; review the updated state")
    run(repo, "diff", "--cached", "--check")
    if run(repo, "diff", "--cached", "--quiet", ok=(0, 1)).returncode == 0:
        raise GitError("No staged changes; an empty commit will not be created")
    message = message.rstrip("\r\n") + "\n"
    run(repo, "commit", "--cleanup=verbatim", "-F", "-", input=message.encode("utf-8"))
    new_head = head(repo)
    parents = git(repo, "show", "-s", "--format=%P", new_head).split()
    actual_tree = git(repo, "show", "-s", "--format=%T", new_head)
    actual_message = git(repo, "log", "-1", "--format=%B")
    expected_parents = [expected_head] if expected_head else []
    if parents != expected_parents or actual_tree != expected_tree or actual_message != message.rstrip("\r\n"):
        raise GitError(f"Commit {new_head} was created but verification failed; preserve the repository and inspect hooks/concurrent changes")
    return {"commit": new_head, "tree": actual_tree, "parents": parents,
            "message": actual_message}


def worktrees(repo):
    """Parse Git's NUL format without breaking spaces, newlines or non-ASCII paths."""
    records = []
    record = {}
    for token in run(repo, "worktree", "list", "--porcelain", "-z").stdout.split(b"\0"):
        if not token:
            if record:
                records.append(record)
                record = {}
            continue
        key, _, value = os.fsdecode(token).partition(" ")
        if key == "worktree":
            record = {"path": str(Path(value).resolve()), "head": None,
                      "branch": None, "bare": False, "locked": False,
                      "prunable": False}
        elif key == "HEAD":
            record["head"] = value
        elif key == "branch":
            record["branch"] = value.removeprefix("refs/heads/")
        elif key in ("bare", "locked", "prunable"):
            record[key] = True
    return records
