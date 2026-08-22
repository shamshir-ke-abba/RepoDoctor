from pathlib import Path

from repodoctor.file_collector import FileCollector


def test_collects_repository_files(tmp_path: Path):
    (tmp_path / "app.py").write_text("print('hello')")
    (tmp_path / "README.md").write_text("# Demo")

    files = list(FileCollector(tmp_path).files())

    assert files == sorted(
        [
            tmp_path / "app.py",
            tmp_path / "README.md",
        ]
    )


def test_collects_files_in_nested_directories(tmp_path: Path):
    package = tmp_path / "package"
    package.mkdir()

    app = package / "app.py"
    readme = package / "README.md"

    app.write_text("print('hello')")
    readme.write_text("# Demo")

    files = list(FileCollector(tmp_path).files())

    assert files == sorted([app, readme])

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

    files = list(FileCollector(tmp_path).files())

    assert files == [tmp_path / "app.py"]


def test_ignores_nested_generated_directories(
    tmp_path: Path,
):
    package = tmp_path / "package"
    package.mkdir()

    valid = package / "valid.py"
    valid.write_text("print('hello')")

    cache = package / "__pycache__"
    cache.mkdir()

    ignored = cache / "ignored.py"
    ignored.write_text("should not be collected")

    files = list(FileCollector(tmp_path).files())

    assert files == [valid]


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


def test_includes_file_at_exact_size_limit(
    tmp_path: Path,
):
    file = tmp_path / "exact.txt"
    file.write_text("12345")

    files = list(
        FileCollector(
            tmp_path,
            max_file_size_bytes=5,
        ).files()
    )

    assert files == [file]


def test_handles_stat_os_error(
    tmp_path: Path,
    monkeypatch,
):
    file = tmp_path / "file.txt"
    file.write_text("hello")

    original_stat = Path.stat

    def failing_stat(self, *args, **kwargs):
        if self == file:
            raise OSError("permission denied")

        return original_stat(self, *args, **kwargs)

    monkeypatch.setattr(Path, "stat", failing_stat)

    files = list(FileCollector(tmp_path).files())

    assert file not in files


def test_collects_python_files_only(tmp_path: Path):
    python_file = tmp_path / "app.py"
    text_file = tmp_path / "README.md"

    python_file.write_text("print('hello')")
    text_file.write_text("# README")

    files = list(
        FileCollector(tmp_path).python_files()
    )

    assert files == [python_file]


def test_python_files_respects_size_limit(
    tmp_path: Path,
):
    small = tmp_path / "small.py"
    large = tmp_path / "large.py"

    small.write_text("x")
    large.write_text("1234567890")

    files = list(
        FileCollector(
            tmp_path,
            max_file_size_bytes=1,
        ).python_files()
    )

    assert files == [small]


def test_python_files_are_sorted(
    tmp_path: Path,
):
    z_file = tmp_path / "z.py"
    a_file = tmp_path / "a.py"
    m_file = tmp_path / "m.py"

    z_file.write_text("z")
    a_file.write_text("a")
    m_file.write_text("m")

    files = list(
        FileCollector(tmp_path).python_files()
    )

    assert files == sorted(
        [
            z_file,
            a_file,
            m_file,
        ]
    )

def test_excludes_configured_directories(
    tmp_path: Path,
):
    (tmp_path / "app.py").write_text("print('hello')")

    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_app.py").write_text(
        "API_KEY = 'fake_secret'"
    )

    collector = FileCollector(
        tmp_path,
        excluded_directories={"tests"},
    )

    files = list(collector.files())

    assert files == [tmp_path / "app.py"]


def test_excludes_configured_directories_nested(
    tmp_path: Path,
):
    package = tmp_path / "package"
    package.mkdir()

    valid = package / "valid.py"
    valid.write_text("print('hello')")

    fixtures = package / "fixtures"
    fixtures.mkdir()

    ignored = fixtures / "ignored.py"
    ignored.write_text("fake secret")

    collector = FileCollector(
        tmp_path,
        excluded_directories={"fixtures"},
    )

    files = list(collector.files())

    assert files == [valid]
