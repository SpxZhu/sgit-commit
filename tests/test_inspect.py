"""Read-only discovery on real repositories, including literal unusual paths."""

import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from git_common import GitError, ensure_ready, run
from inspect_repo import inspect


class InspectTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="sgit-inspect-")
        self.addCleanup(self.temporary.cleanup)
        self.repo = Path(self.temporary.name)
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Sgit Test")
        self.git("config", "user.email", "sgit@example.invalid")
        self.git("config", "commit.gpgsign", "false")
        self.git("config", "core.autocrlf", "false")
        self.write("原 文件.txt", "base\n")
        self.write("pick[1].txt", "old literal\n")
        self.write("pick1.txt", "old glob\n")
        self.git("add", "--all")
        self.git("commit", "-m", "initial")

    def git(self, *args):
        return subprocess.run(["git", "--no-optional-locks", "-C", str(self.repo), *args], check=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout

    def write(self, name, contents):
        (self.repo / name).write_text(contents, encoding="utf-8", newline="\n")

    def test_snapshot_does_not_change_index_head_or_worktree(self):
        self.git("mv", "原 文件.txt", "重命名 文件.txt")
        self.write("重命名 文件.txt", "base\nunstaged\n")
        self.write("未跟踪 [a].txt", "new\n")
        index = self.repo / ".git/index"
        before = (hashlib.sha256(index.read_bytes()).digest(), index.stat().st_mtime_ns,
                  self.git("rev-parse", "HEAD"), self.git("status", "--porcelain=v1", "-z"))
        result = inspect(self.repo, include_worktrees=True)
        after = (hashlib.sha256(index.read_bytes()).digest(), index.stat().st_mtime_ns,
                  self.git("rev-parse", "HEAD"), self.git("status", "--porcelain=v1", "-z"))
        self.assertEqual(before, after)
        renamed = next(item for item in result["status"] if item["x"] == "R")
        self.assertEqual((renamed["path"], renamed["original"], renamed["y"]),
                         ("重命名 文件.txt", "原 文件.txt", "M"))
        self.assertTrue(any(item["path"] == "未跟踪 [a].txt" and item["x"] == "?"
                            for item in result["status"]))
        self.assertEqual(result["worktrees"][0]["branch"], "main")

    def test_literal_filter_and_complete_patch(self):
        self.write("pick[1].txt", "literal result\n")
        self.write("pick1.txt", "glob result\n")
        result = inspect(self.repo, paths=["pick[1].txt"], patch=True)
        self.assertIn("+literal result", result["unstaged_patch"])
        self.assertNotIn("glob result", result["unstaged_patch"])

    def test_no_commit_repository_and_special_index(self):
        empty = self.repo / "empty"
        empty.mkdir()
        subprocess.run(["git", "init", "-b", "main", str(empty)], check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertIsNone(inspect(empty)["head"])
        self.git("update-index", "--assume-unchanged", "pick1.txt")
        with self.assertRaisesRegex(GitError, "assume-unchanged"):
            ensure_ready(self.repo)

    def test_whitespace_failure_includes_git_diagnostic(self):
        self.write("pick1.txt", "trailing whitespace \n")
        self.git("add", "pick1.txt")
        with self.assertRaisesRegex(GitError, "trailing whitespace"):
            run(self.repo, "diff", "--cached", "--check")


if __name__ == "__main__":
    unittest.main()
