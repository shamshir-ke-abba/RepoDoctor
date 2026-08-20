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

def test_non_git_directory_returns_default_report(tmp_path: Path):
    result = GitAnalyzer().analyze(tmp_path)

    assert result.is_repo is False
    assert result.branch == ""
    assert result.commits == 0
    assert result.clean is True
    assert result.untracked == 0
    assert result.modified == 0
    assert result.remote is False


def test_detects_current_branch(tmp_path: Path):
    git(tmp_path, "init", "-b", "main")

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

    assert result.branch == "main"


def test_counts_untracked_files(tmp_path: Path):
    git(tmp_path, "init")

    (tmp_path / "one.py").write_text("one")
    (tmp_path / "two.py").write_text("two")

    result = GitAnalyzer().analyze(tmp_path)

    assert result.untracked == 2
    assert result.modified == 0
    assert result.clean is False


def test_counts_modified_files(tmp_path: Path):
    git(tmp_path, "init")

    file = tmp_path / "hello.py"
    file.write_text("original")

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

    file.write_text("modified")

    result = GitAnalyzer().analyze(tmp_path)

    assert result.modified == 1
    assert result.untracked == 0
    assert result.clean is False


def test_counts_untracked_and_modified_files(tmp_path: Path):
    git(tmp_path, "init")

    tracked = tmp_path / "tracked.py"
    tracked.write_text("original")

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

    tracked.write_text("modified")
    (tmp_path / "untracked.py").write_text("new")

    result = GitAnalyzer().analyze(tmp_path)

    assert result.untracked == 1
    assert result.modified == 1
    assert result.clean is False


def test_detects_remote(tmp_path: Path):
    git(tmp_path, "init")

    git(
        tmp_path,
        "remote",
        "add",
        "origin",
        "https://example.com/test.git",
    )

    result = GitAnalyzer().analyze(tmp_path)

    assert result.remote is True


def test_detects_repository_without_remote(tmp_path: Path):
    git(tmp_path, "init")

    result = GitAnalyzer().analyze(tmp_path)

    assert result.remote is False


def test_uses_unknown_when_branch_command_returns_empty(
    tmp_path: Path,
    monkeypatch,
):
    analyzer = GitAnalyzer()

    def fake_run(root: Path, command: list[str]) -> str:
        if command == [
            "git",
            "rev-parse",
            "--is-inside-work-tree",
        ]:
            return "true"

        if command == [
            "git",
            "branch",
            "--show-current",
        ]:
            return ""

        if command == [
            "git",
            "rev-list",
            "--count",
            "HEAD",
        ]:
            return "3"

        return ""

    monkeypatch.setattr(analyzer, "_run", fake_run)

    result = analyzer.analyze(tmp_path)

    assert result.is_repo is True
    assert result.branch == "unknown"
    assert result.commits == 3


def test_invalid_commit_count_returns_zero(
    tmp_path: Path,
    monkeypatch,
):
    analyzer = GitAnalyzer()

    def fake_run(root: Path, command: list[str]) -> str:
        if command == [
            "git",
            "rev-parse",
            "--is-inside-work-tree",
        ]:
            return "true"

        if command == [
            "git",
            "branch",
            "--show-current",
        ]:
            return "main"

        if command == [
            "git",
            "rev-list",
            "--count",
            "HEAD",
        ]:
            return "not-a-number"

        return ""

    monkeypatch.setattr(analyzer, "_run", fake_run)

    result = analyzer.analyze(tmp_path)

    assert result.commits == 0


def test_run_returns_empty_on_command_failure(
    tmp_path: Path,
    monkeypatch,
):
    analyzer = GitAnalyzer()

    class FailedResult:
        returncode = 1
        stdout = "unexpected output"

    def fake_subprocess_run(*args, **kwargs):
        return FailedResult()

    monkeypatch.setattr(
        subprocess,
        "run",
        fake_subprocess_run,
    )

    result = analyzer._run(
        tmp_path,
        ["git", "status"],
    )

    assert result == ""


def test_run_returns_empty_on_os_error(
    tmp_path: Path,
    monkeypatch,
):
    analyzer = GitAnalyzer()

    def fake_subprocess_run(*args, **kwargs):
        raise OSError("git unavailable")

    monkeypatch.setattr(
        subprocess,
        "run",
        fake_subprocess_run,
    )

    result = analyzer._run(
        tmp_path,
        ["git", "status"],
    )

    assert result == ""


def test_run_returns_empty_on_subprocess_error(
    tmp_path: Path,
    monkeypatch,
):
    analyzer = GitAnalyzer()

    def fake_subprocess_run(*args, **kwargs):
        raise subprocess.SubprocessError("command failed")

    monkeypatch.setattr(
        subprocess,
        "run",
        fake_subprocess_run,
    )

    result = analyzer._run(
        tmp_path,
        ["git", "status"],
    )

    assert result == ""


def test_to_int_converts_valid_integer():
    analyzer = GitAnalyzer()

    assert analyzer._to_int("42") == 42


def test_to_int_returns_zero_for_invalid_value():
    analyzer = GitAnalyzer()

    assert analyzer._to_int("invalid") == 0
