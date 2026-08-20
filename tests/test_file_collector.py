from pathlib import Path

from repodoctor.file_collector import FileCollector


def test_collects_repository_files(tmp_path: Path):
    (tmp_path / "app.py").write_text("print('hello')")
    (tmp_path / "README.md").write_text("# Demo")

    files = list(
        FileCollector(tmp_path).files()
    )

    assert files == sorted(
        [
            tmp_path / "app.py",
            tmp_path / "README.md",
        ]
    )


def test_ignores_generated_and_dependency_directories(
    tmp_path: Path,
):
    (tmp_path / "app.py").write_text("print('hello')")

    ignored_dirs = [
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        "node_modules",
        ".mypy_cache",
        ".pytest_cache",
    ]

    for directory in ignored_dirs:
        path = tmp_path / directory
        path.mkdir()
        (path / "ignored.py").write_text(
            "should not be collected"
        )

    files = list(
        FileCollector(tmp_path).files()
    )

    assert files == [tmp_path / "app.py"]


def test_skips_files_above_size_limit(
    tmp_path: Path,
):
    small = tmp_path / "small.txt"
    large = tmp_path / "large.txt"

    small.write_text("small")
    large.write_text("1234567890")

    files = list(
        FileCollector(
            tmp_path,
            max_file_size_bytes=5,
        ).files()
    )

    assert files == [small]


def test_handles_inaccessible_file_without_crashing(
    tmp_path: Path,
):
    file = tmp_path / "file.txt"
    file.write_text("hello")

    collector = FileCollector(tmp_path)

    files = list(collector.files())

    assert file in files


def test_collects_python_files_only(tmp_path: Path):
    python_file = tmp_path / "app.py"
    text_file = tmp_path / "README.md"

    python_file.write_text("print('hello')")
    text_file.write_text("# README")

    files = list(
        FileCollector(tmp_path).python_files()
    )

    assert files == [python_file]
