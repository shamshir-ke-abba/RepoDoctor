from repodoctor.models import (
    FunctionReport,
    GitReport,
    PythonFileReport,
    RepositoryReport,
)


def test_function_report_lines():
    report = FunctionReport(
        name="example",
        file="app.py",
        line=10,
        end_line=19,
        complexity=3,
        arguments=2,
        nesting_depth=1,
    )

    assert report.lines == 10


def test_function_report_single_line():
    report = FunctionReport(
        name="example",
        file="app.py",
        line=10,
        end_line=10,
        complexity=1,
        arguments=0,
        nesting_depth=0,
    )

    assert report.lines == 1


def test_python_file_report_defaults():
    report = PythonFileReport(
        path="app.py",
        lines=20,
        functions=2,
        classes=1,
        todos=3,
    )

    assert report.functions_report == []


def test_python_file_report_stores_functions():
    function = FunctionReport(
        name="example",
        file="app.py",
        line=1,
        end_line=5,
        complexity=1,
        arguments=0,
        nesting_depth=0,
    )

    report = PythonFileReport(
        path="app.py",
        lines=10,
        functions=1,
        classes=0,
        todos=0,
        functions_report=[function],
    )

    assert report.functions_report == [function]


def test_git_report_defaults():
    report = GitReport()

    assert report.is_repo is False
    assert report.branch == ""
    assert report.commits == 0
    assert report.clean is True
    assert report.untracked == 0
    assert report.modified == 0
    assert report.remote is False


def test_repository_report_defaults():
    report = RepositoryReport(path=".")

    assert report.path == "."
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

    assert report.has_readme is False
    assert report.has_gitignore is False
    assert report.is_git_repo is False

    assert report.recommendations == []
    assert report.warnings == []
    assert report.successes == []
    assert report.health_score == 100


def test_repository_report_has_independent_mutable_defaults():
    first = RepositoryReport(path=".")
    second = RepositoryReport(path=".")

    first.large_files.append("app.py")
    first.warnings.append("warning")

    assert second.large_files == []
    assert second.warnings == []


def test_repository_report_has_independent_git_reports():
    first = RepositoryReport(path=".")
    second = RepositoryReport(path=".")

    first.git.is_repo = True
    first.git.branch = "master"

    assert second.git.is_repo is False
    assert second.git.branch == ""


def test_repository_report_accepts_nested_reports():
    function = FunctionReport(
        name="example",
        file="app.py",
        line=1,
        end_line=3,
        complexity=2,
        arguments=1,
        nesting_depth=0,
    )

    report = RepositoryReport(
        path=".",
        python_files=1,
        total_lines=3,
        total_functions=1,
        complex_functions=[function],
        large_functions=[function],
    )

    assert report.python_files == 1
    assert report.total_lines == 3
    assert report.total_functions == 1
    assert report.complex_functions == [function]
    assert report.large_functions == [function]
