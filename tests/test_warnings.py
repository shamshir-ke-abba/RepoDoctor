from repodoctor.models import RepositoryReport
from repodoctor.warnings import WarningEngine


def clean_report():
    report = RepositoryReport(path=".")

    report.has_readme = True
    report.has_gitignore = True
    report.git.is_repo = True
    report.git.clean = True
    report.git.remote = True

    return report


def test_no_warnings_for_clean_report():
    report = clean_report()

    assert WarningEngine().generate(report) == []


def test_security_warning():
    report = clean_report()

    report.security_findings = [object(), object()]

    warnings = WarningEngine().generate(report)

    assert warnings == ["2 security finding(s)"]


def test_code_quality_warnings():
    report = clean_report()

    report.complex_functions = [object()]
    report.large_functions = [object()]
    report.deep_functions = [object()]
    report.argument_heavy_functions = [object()]
    report.large_files = [object()]

    warnings = WarningEngine().generate(report)

    assert "1 high-complexity function(s)" in warnings
    assert "1 large function(s)" in warnings
    assert "1 deeply nested function(s)" in warnings
    assert "1 function(s) with too many arguments" in warnings
    assert "1 large file(s)" in warnings


def test_todo_warning():
    report = clean_report()

    report.total_todos = 11

    warnings = WarningEngine().generate(report)

    assert "11 TODO/FIXME comment(s)" in warnings


def test_missing_readme_warning():
    report = clean_report()

    report.has_readme = False

    warnings = WarningEngine().generate(report)

    assert "README is missing" in warnings


def test_missing_gitignore_warning():
    report = clean_report()

    report.has_gitignore = False

    warnings = WarningEngine().generate(report)

    assert ".gitignore is missing" in warnings


def test_dirty_git_warning():
    report = clean_report()

    report.git.clean = False

    warnings = WarningEngine().generate(report)

    assert "Git working tree has changes" in warnings


def test_missing_git_remote_warning():
    report = clean_report()

    report.git.remote = False

    warnings = WarningEngine().generate(report)

    assert "Git remote is not configured" in warnings


def test_not_git_repository_warning():
    report = clean_report()

    report.git.is_repo = False

    warnings = WarningEngine().generate(report)

    assert "Git repository is not configured" in warnings


def test_multiple_warning_categories():
    report = clean_report()

    report.security_findings = [object()]
    report.complex_functions = [object()]
    report.total_todos = 11
    report.has_readme = False
    report.git.clean = False

    warnings = WarningEngine().generate(report)

    assert "1 security finding(s)" in warnings
    assert "1 high-complexity function(s)" in warnings
    assert "11 TODO/FIXME comment(s)" in warnings
    assert "README is missing" in warnings
    assert "Git working tree has changes" in warnings


def test_ten_todos_do_not_trigger_warning():
    report = clean_report()
    report.total_todos = 10

    assert WarningEngine().generate(report) == []


def test_todo_threshold_is_strictly_greater_than_ten():
    report = clean_report()
    report.total_todos = 11

    warnings = WarningEngine().generate(report)

    assert warnings == [
        "11 TODO/FIXME comment(s)"
    ]


def test_non_git_repository_only_reports_git_configuration_warning():
    report = clean_report()
    report.git.is_repo = False
    report.git.clean = False
    report.git.remote = False

    warnings = WarningEngine().generate(report)

    assert warnings == [
        "Git repository is not configured"
    ]


def test_all_warning_categories_preserve_order():
    report = clean_report()

    report.security_findings = [object(), object()]
    report.complex_functions = [object()]
    report.large_functions = [object()]
    report.deep_functions = [object()]
    report.argument_heavy_functions = [object()]
    report.large_files = [object()]
    report.total_todos = 11
    report.has_readme = False
    report.has_gitignore = False
    report.git.clean = False
    report.git.remote = False

    warnings = WarningEngine().generate(report)

    assert warnings == [
        "2 security finding(s)",
        "1 high-complexity function(s)",
        "1 large function(s)",
        "1 deeply nested function(s)",
        "1 function(s) with too many arguments",
        "1 large file(s)",
        "11 TODO/FIXME comment(s)",
        "README is missing",
        ".gitignore is missing",
        "Git working tree has changes",
        "Git remote is not configured",
    ]
