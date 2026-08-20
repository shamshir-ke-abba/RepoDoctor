import json
from pathlib import Path

from repodoctor.models import (
    FunctionReport,
    GitReport,
    RepositoryReport,
)
from repodoctor.reporting.json import JSONReporter
from repodoctor.reporting.terminal import TerminalReporter
from repodoctor.analyzers.security import SecurityFinding


def make_report() -> RepositoryReport:
    report = RepositoryReport(
        path="/tmp/project",
        python_files=3,
        total_lines=120,
        total_functions=8,
        total_classes=2,
        total_todos=4,
        has_readme=True,
        has_gitignore=True,
        is_git_repo=True,
        health_score=87,
    )

    report.git = GitReport(
        is_repo=True,
        branch="main",
        commits=12,
        clean=True,
        untracked=2,
        modified=1,
        remote=True,
    )

    function = FunctionReport(
        name="process",
        file="/tmp/project/main.py",
        line=10,
        end_line=20,
        complexity=8,
        arguments=7,
        nesting_depth=5,
    )

    report.large_files = [
        "/tmp/project/main.py (600 lines)",
    ]
    report.complex_functions = [function]
    report.large_functions = [function]
    report.deep_functions = [function]
    report.argument_heavy_functions = [function]

    report.security_findings = [
        SecurityFinding(
            file="/tmp/project/config.py",
            line=3,
            rule="API_KEY",
            severity="HIGH",
            message="Potential hardcoded API key or token",
        )
    ]

    report.warnings = [
        "Repository contains security findings",
    ]

    report.recommendations = [
        "Reduce function complexity",
    ]

    return report


def test_json_reporter_outputs_valid_json(
    capsys,
):
    report = make_report()

    JSONReporter().print_report(report)

    output = capsys.readouterr().out
    data = json.loads(output)

    assert data["path"] == "/tmp/project"
    assert data["python_files"] == 3
    assert data["total_lines"] == 120
    assert data["health_score"] == 87


def test_json_reporter_serializes_git_report(
    capsys,
):
    report = make_report()

    JSONReporter().print_report(report)

    data = json.loads(
        capsys.readouterr().out
    )

    assert data["git"]["is_repo"] is True
    assert data["git"]["branch"] == "main"
    assert data["git"]["commits"] == 12
    assert data["git"]["clean"] is True
    assert data["git"]["remote"] is True


def test_json_reporter_serializes_function_reports(
    capsys,
):
    report = make_report()

    JSONReporter().print_report(report)

    data = json.loads(
        capsys.readouterr().out
    )

    function = data["complex_functions"][0]

    assert function["name"] == "process"
    assert function["line"] == 10
    assert function["end_line"] == 20
    assert function["complexity"] == 8
    assert function["arguments"] == 7
    assert function["nesting_depth"] == 5


def test_json_reporter_serializes_security_findings(
    capsys,
):
    report = make_report()

    JSONReporter().print_report(report)

    data = json.loads(
        capsys.readouterr().out
    )

    finding = data["security_findings"][0]

    assert finding["severity"] == "HIGH"
    assert finding["file"] == "/tmp/project/config.py"
    assert finding["line"] == 3


def test_json_reporter_handles_empty_report(
    capsys,
):
    report = RepositoryReport(path=".")

    JSONReporter().print_report(report)

    data = json.loads(
        capsys.readouterr().out
    )

    assert data["path"] == "."
    assert data["python_files"] == 0
    assert data["git"]["is_repo"] is False
    assert data["warnings"] == []
    assert data["recommendations"] == []


def test_terminal_prints_header(
    capsys,
):
    report = RepositoryReport(
        path="/tmp/project",
    )

    TerminalReporter()._print_header(report)

    output = capsys.readouterr().out

    assert "REPO DOCTOR" in output
    assert "Repository Health Report" in output
    assert "Repository: /tmp/project" in output


def test_terminal_prints_project_section(
    capsys,
):
    report = make_report()

    TerminalReporter()._print_project(report)

    output = capsys.readouterr().out

    assert "PROJECT" in output
    assert "Python files       3" in output
    assert "Total lines        120" in output
    assert "Functions          8" in output
    assert "Classes            2" in output
    assert "TODO/FIXME         4" in output


def test_terminal_prints_structure_status(
    capsys,
):
    report = make_report()

    TerminalReporter()._print_structure(report)

    output = capsys.readouterr().out

    assert "STRUCTURE" in output
    assert "✓ README" in output
    assert "✓ .gitignore" in output
    assert "✓ Git repository" in output


def test_terminal_prints_missing_structure_status(
    capsys,
):
    report = RepositoryReport(path=".")

    TerminalReporter()._print_structure(report)

    output = capsys.readouterr().out

    assert "⚠ README" in output
    assert "⚠ .gitignore" in output
    assert "⚠ Git repository" in output


def test_terminal_prints_git_health(
    capsys,
):
    report = make_report()

    TerminalReporter()._print_git(report)

    output = capsys.readouterr().out

    assert "GIT HEALTH" in output
    assert "Branch             main" in output
    assert "Commits            12" in output
    assert "Working tree       CLEAN" in output
    assert "Untracked files    2" in output
    assert "Modified files     1" in output
    assert "Remote             ✓ configured" in output


def test_terminal_prints_non_git_message(
    capsys,
):
    report = RepositoryReport(path=".")

    TerminalReporter()._print_git(report)

    output = capsys.readouterr().out

    assert "GIT HEALTH" in output
    assert "⚠ Not a Git repository" in output


def test_terminal_prints_dirty_git_state(
    capsys,
):
    report = make_report()
    report.git.clean = False
    report.git.remote = False

    TerminalReporter()._print_git(report)

    output = capsys.readouterr().out

    assert "Working tree       DIRTY" in output
    assert "Remote             ⚠ not configured" in output


def test_terminal_prints_warnings(
    capsys,
):
    report = make_report()

    TerminalReporter()._print_warnings(report)

    output = capsys.readouterr().out

    assert "WARNINGS" in output
    assert "⚠ Repository contains security findings" in output


def test_terminal_prints_no_warnings(
    capsys,
):
    report = RepositoryReport(path=".")

    TerminalReporter()._print_warnings(report)

    output = capsys.readouterr().out

    assert "✓ No warnings detected" in output


def test_terminal_prints_large_files(
    capsys,
):
    report = make_report()

    TerminalReporter()._print_large_files(report)

    output = capsys.readouterr().out

    assert "LARGE FILES" in output
    assert "⚠ /tmp/project/main.py (600 lines)" in output


def test_terminal_prints_no_large_files(
    capsys,
):
    report = RepositoryReport(path=".")

    TerminalReporter()._print_large_files(report)

    output = capsys.readouterr().out

    assert "✓ No unusually large files" in output


def test_terminal_prints_complexity(
    capsys,
):
    report = make_report()

    TerminalReporter()._print_complexity(report)

    output = capsys.readouterr().out

    assert "COMPLEXITY" in output
    assert "/tmp/project/main.py:10" in output
    assert "process() complexity: 8" in output


def test_terminal_prints_function_size(
    capsys,
):
    report = make_report()

    TerminalReporter()._print_function_size(report)

    output = capsys.readouterr().out

    assert "FUNCTION SIZE" in output
    assert "process() 11 lines" in output


def test_terminal_prints_nesting(
    capsys,
):
    report = make_report()

    TerminalReporter()._print_nesting(report)

    output = capsys.readouterr().out

    assert "NESTING" in output
    assert "process() nesting depth: 5" in output


def test_terminal_prints_arguments(
    capsys,
):
    report = make_report()

    TerminalReporter()._print_arguments(report)

    output = capsys.readouterr().out

    assert "ARGUMENTS" in output
    assert "process() 7 arguments" in output


def test_terminal_prints_security_findings(
    capsys,
):
    report = make_report()

    TerminalReporter()._print_security(report)

    output = capsys.readouterr().out

    assert "SECURITY" in output
    assert "[HIGH]" in output
    assert "/tmp/project/config.py:3" in output
    assert "Potential hardcoded API key or token" in output


def test_terminal_prints_no_security_findings(
    capsys,
):
    report = RepositoryReport(path=".")

    TerminalReporter()._print_security(report)

    output = capsys.readouterr().out

    assert "✓ No obvious security issues detected" in output


def test_terminal_prints_recommendations_and_score(
    capsys,
):
    report = make_report()

    TerminalReporter()._print_recommendations(report)

    output = capsys.readouterr().out

    assert "RECOMMENDATIONS" in output
    assert "→ Reduce function complexity" in output
    assert "HEALTH SCORE: 87/100" in output


def test_terminal_prints_no_recommendations(
    capsys,
):
    report = RepositoryReport(path=".")

    TerminalReporter()._print_recommendations(report)

    output = capsys.readouterr().out

    assert "✓ No recommendations" in output
    assert "HEALTH SCORE" not in output


def test_terminal_prints_score(
    capsys,
):
    report = RepositoryReport(
        path=".",
        health_score=73,
    )

    TerminalReporter()._print_score(report)

    output = capsys.readouterr().out

    assert "HEALTH SCORE: 73/100" in output


def test_terminal_prints_full_report(
    capsys,
):
    report = make_report()

    TerminalReporter().print_report(report)

    output = capsys.readouterr().out

    expected_sections = (
        "REPO DOCTOR",
        "PROJECT",
        "STRUCTURE",
        "GIT HEALTH",
        "WARNINGS",
        "LARGE FILES",
        "COMPLEXITY",
        "FUNCTION SIZE",
        "NESTING",
        "ARGUMENTS",
        "SECURITY",
        "RECOMMENDATIONS",
        "HEALTH SCORE: 87/100",
    )

    for section in expected_sections:
        assert section in output


def test_terminal_empty_report_prints_clean_sections(
    capsys,
):
    report = RepositoryReport(path=".")

    TerminalReporter().print_report(report)

    output = capsys.readouterr().out

    assert "REPO DOCTOR" in output
    assert "✓ No warnings detected" in output
    assert "✓ No unusually large files" in output
    assert "✓ No highly complex functions" in output
    assert "✓ No unusually large functions" in output
    assert "✓ No deeply nested functions" in output
    assert "✓ No functions with too many arguments" in output
    assert "✓ No obvious security issues detected" in output
    assert "✓ No recommendations" in output
