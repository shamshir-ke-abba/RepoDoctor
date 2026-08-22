from pathlib import Path

from repodoctor.config import ScanConfig
from repodoctor.scanner import RepositoryScanner


def test_scanner_builds_complete_report(tmp_path: Path):
    (tmp_path / "README.md").write_text("# Test")
    (tmp_path / ".gitignore").write_text("__pycache__/")
    (tmp_path / "main.py").write_text(
        """
# TODO: improve this

def hello(name):
    if name:
        return name
    return "hello"
"""
    )

    report = RepositoryScanner(
        tmp_path,
        ScanConfig(),
    ).scan()

    assert report.path == str(tmp_path.resolve())
    assert report.python_files == 1
    assert report.total_lines > 0
    assert report.total_functions == 1
    assert report.total_todos == 1
    assert report.has_readme is True
    assert report.has_gitignore is True
    assert isinstance(report.warnings, list)
    assert isinstance(report.recommendations, list)
    assert isinstance(report.health_score, int)


def test_scanner_counts_python_project_stats(tmp_path: Path):
    (tmp_path / "one.py").write_text(
        """
class Example:
    def first(self):
        return 1
"""
    )

    (tmp_path / "two.py").write_text(
        """
def second():
    return 2
"""
    )

    report = RepositoryScanner(
        tmp_path,
        ScanConfig(),
    ).scan()

    assert report.python_files == 2
    assert report.total_functions == 2
    assert report.total_classes == 1
    assert report.total_lines > 0


def test_scanner_detects_large_file(tmp_path: Path):
    (tmp_path / "large.py").write_text(
        "\n".join(
            "value = 1"
            for _ in range(10)
        )
    )

    config = ScanConfig(
        large_file_threshold=10,
    )

    report = RepositoryScanner(
        tmp_path,
        config,
    ).scan()

    assert len(report.large_files) == 1
    assert "large.py" in report.large_files[0]


def test_scanner_detects_large_function(tmp_path: Path):
    body = "\n".join(
        f"    value_{index} = {index}"
        for index in range(10)
    )

    (tmp_path / "large_function.py").write_text(
        "def large():\n"
        + body
        + "\n"
    )

    config = ScanConfig(
        large_function_threshold=5,
    )

    report = RepositoryScanner(
        tmp_path,
        config,
    ).scan()

    assert len(report.large_functions) == 1
    assert report.large_functions[0].name == "large"


def test_scanner_detects_complex_function(tmp_path: Path):
    (tmp_path / "complex.py").write_text(
        """
def complex_function(value):
    if value:
        for item in value:
            if item:
                while item:
                    break
    return value
"""
    )

    config = ScanConfig(
        complexity_threshold=4,
    )

    report = RepositoryScanner(
        tmp_path,
        config,
    ).scan()

    assert len(report.complex_functions) == 1
    assert report.complex_functions[0].name == "complex_function"


def test_scanner_detects_deep_function(tmp_path: Path):
    (tmp_path / "deep.py").write_text(
        """
def deeply_nested(value):
    if value:
        for item in value:
            while item:
                with open("file.txt") as file:
                    return file.read()
"""
    )

    config = ScanConfig(
        nesting_threshold=4,
    )

    report = RepositoryScanner(
        tmp_path,
        config,
    ).scan()

    assert len(report.deep_functions) == 1
    assert report.deep_functions[0].name == "deeply_nested"


def test_scanner_detects_argument_heavy_function(
    tmp_path: Path,
):
    (tmp_path / "arguments.py").write_text(
        """
def configure(a, b, c, d, e, f):
    return True
"""
    )

    config = ScanConfig(
        argument_threshold=6,
    )

    report = RepositoryScanner(
        tmp_path,
        config,
    ).scan()

    assert len(report.argument_heavy_functions) == 1
    assert (
        report.argument_heavy_functions[0].name
        == "configure"
    )


def test_scanner_detects_security_findings(
    tmp_path: Path,
):
    (tmp_path / "config.py").write_text(
        'API_KEY = "real_secret_key_12345678"\n'
    )

    report = RepositoryScanner(
        tmp_path,
        ScanConfig(),
    ).scan()

    assert len(report.security_findings) == 1
    assert report.security_findings[0].severity == "HIGH"


def test_scanner_detects_git_repository(tmp_path: Path):
    import subprocess

    subprocess.run(
        ["git", "init"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )

    report = RepositoryScanner(
        tmp_path,
        ScanConfig(),
    ).scan()

    assert report.is_git_repo is True
    assert report.git.is_repo is True


def test_scanner_non_git_repository(
    tmp_path: Path,
):
    report = RepositoryScanner(
        tmp_path,
        ScanConfig(),
    ).scan()

    assert report.is_git_repo is False
    assert report.git.is_repo is False


def test_scanner_handles_empty_repository(
    tmp_path: Path,
):
    report = RepositoryScanner(
        tmp_path,
        ScanConfig(),
    ).scan()

    assert report.python_files == 0
    assert report.total_lines == 0
    assert report.total_functions == 0
    assert report.total_classes == 0
    assert report.total_todos == 0
    assert report.large_files == []
    assert report.complex_functions == []
    assert report.large_functions == []
    assert report.deep_functions == []
    assert report.argument_heavy_functions == []
    assert report.security_findings == []


def test_scanner_uses_custom_thresholds(
    tmp_path: Path,
):
    (tmp_path / "main.py").write_text(
        """
def hello(a, b):
    if a:
        return b
    return a
"""
    )

    config = ScanConfig(
        complexity_threshold=2,
        argument_threshold=2,
    )

    report = RepositoryScanner(
        tmp_path,
        config,
    ).scan()

    assert len(report.complex_functions) == 1
    assert len(report.argument_heavy_functions) == 1


def test_scanner_generates_warnings_and_recommendations(
    tmp_path: Path,
):
    (tmp_path / "main.py").write_text(
        """
def hello():
    # TODO: fix this
    return True
"""
    )

    report = RepositoryScanner(
        tmp_path,
        ScanConfig(),
    ).scan()

    assert isinstance(report.warnings, list)
    assert isinstance(report.recommendations, list)


def test_python_files_returns_collector_python_files(
    tmp_path: Path,
):
    (tmp_path / "main.py").write_text("print('hello')")

    scanner = RepositoryScanner(
        tmp_path,
        ScanConfig(),
    )

    files = list(scanner._python_files())

    assert files == [tmp_path / "main.py"]


def test_scanner_resolves_root_path(tmp_path: Path):
    scanner = RepositoryScanner(
        tmp_path / ".",
        ScanConfig(),
    )

    assert scanner.root == tmp_path.resolve()

def test_scanner_loads_config_from_pyproject(
    tmp_path: Path,
):
    (tmp_path / "pyproject.toml").write_text(
        """
[tool.repodoctor]
complexity_threshold = 2
argument_threshold = 2
large_file_threshold = 10
""".strip()
    )

    (tmp_path / "main.py").write_text(
        """
def hello(a, b):
    if a:
        return b
    return a
"""
    )

    scanner = RepositoryScanner(tmp_path)

    assert scanner.config.complexity_threshold == 2
    assert scanner.config.argument_threshold == 2
    assert scanner.config.large_file_threshold == 10

    report = scanner.scan()

    assert len(report.complex_functions) == 1
    assert len(report.argument_heavy_functions) == 1

def test_scanner_uses_configured_excluded_directories(
    tmp_path: Path,
):
    config = ScanConfig(
        excluded_directories={"tests"},
    )

    scanner = RepositoryScanner(
        tmp_path,
        config,
    )

    assert scanner.file_collector.excluded_directories == {
        "tests"
    }
