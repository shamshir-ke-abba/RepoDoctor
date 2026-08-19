import subprocess
from pathlib import Path

from repodoctor.analyzers.git import GitAnalyzer


def git(root: Path, *args: str):
    subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
    )


def test_detects_git_repository(tmp_path: Path):
    git(tmp_path, "init")

    result = GitAnalyzer().analyze(tmp_path)

    assert result.is_repo is True


def test_detects_clean_repository(tmp_path: Path):
    git(tmp_path, "init")

    file = tmp_path / "hello.py"
    file.write_text("print('hello')")

    git(tmp_path, "add", ".")
    git(
        tmp_path,
        "-c",
        "user.name=Test",
        "-c",
        "user.email=test@example.com",
        "commit",
        "-m",
        "Initial commit",
    )

    result = GitAnalyzer().analyze(tmp_path)

    assert result.is_repo is True
    assert result.commits == 1
    assert result.clean is True
