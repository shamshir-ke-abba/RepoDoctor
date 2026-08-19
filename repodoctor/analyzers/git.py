import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class GitReport:
    is_repo: bool = False
    branch: str = ""
    commits: int = 0
    clean: bool = True
    untracked: int = 0
    modified: int = 0
    remote: bool = False


class GitAnalyzer:
    """Analyze Git repository health."""

    def analyze(self, root: Path) -> GitReport:

        if not self._is_git_repo(root):
            return GitReport()

        branch = self._run(
            root,
            ["git", "branch", "--show-current"],
        )

        commit_count = self._run(
            root,
            ["git", "rev-list", "--count", "HEAD"],
        )

        status = self._run(
            root,
            ["git", "status", "--porcelain"],
        )

        remote = self._run(
            root,
            ["git", "remote"],
        )

        untracked = 0
        modified = 0

        for line in status.splitlines():

            if line.startswith("??"):
                untracked += 1

            else:
                modified += 1

        return GitReport(
            is_repo=True,
            branch=branch or "unknown",
            commits=self._to_int(commit_count),
            clean=not status.strip(),
            untracked=untracked,
            modified=modified,
            remote=bool(remote.strip()),
        )

    def _is_git_repo(
        self,
        root: Path,
    ) -> bool:

        result = self._run(
            root,
            [
                "git",
                "rev-parse",
                "--is-inside-work-tree",
            ],
        )

        return result.strip() == "true"

    def _run(
        self,
        root: Path,
        command: list[str],
    ) -> str:

        try:

            result = subprocess.run(
                command,
                cwd=root,
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode != 0:
                return ""

            return result.stdout.strip()

        except (
            OSError,
            subprocess.SubprocessError,
        ):
            return ""

    def _to_int(
        self,
        value: str,
    ) -> int:

        try:
            return int(value)

        except ValueError:
            return 0
