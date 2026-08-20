from repodoctor.models import RepositoryReport
from repodoctor.recommendations import RecommendationEngine


def clean_report() -> RepositoryReport:
    report = RepositoryReport(path=".")

    report.has_readme = True
    report.has_gitignore = True

    report.git.is_repo = True
    report.git.clean = True
    report.git.remote = True

    return report


def test_no_recommendations_for_clean_report():
    report = clean_report()

    assert RecommendationEngine().generate(report) == []


def test_security_recommendation():
    report = clean_report()
    report.security_findings = [object()]

    recommendations = RecommendationEngine().generate(report)

    assert recommendations == [
        "Move hardcoded secrets to "
        "environment variables or a "
        "secret manager."
    ]


def test_complexity_recommendation():
    report = clean_report()
    report.complex_functions = [object()]

    recommendations = RecommendationEngine().generate(report)

    assert recommendations == [
        "Split high-complexity functions "
        "into smaller functions with "
        "single responsibilities."
    ]


def test_function_size_recommendation():
    report = clean_report()
    report.large_functions = [object()]

    recommendations = RecommendationEngine().generate(report)

    assert recommendations == [
        "Break large functions into "
        "smaller logical units."
    ]


def test_nesting_recommendation():
    report = clean_report()
    report.deep_functions = [object()]

    recommendations = RecommendationEngine().generate(report)

    assert recommendations == [
        "Reduce deep nesting by using "
        "early returns and guard clauses."
    ]


def test_argument_recommendation():
    report = clean_report()
    report.argument_heavy_functions = [object()]

    recommendations = RecommendationEngine().generate(report)

    assert recommendations == [
        "Reduce functions with many "
        "arguments by grouping related "
        "data into objects or dataclasses."
    ]


def test_missing_documentation_recommendations():
    report = clean_report()

    report.has_readme = False
    report.has_gitignore = False

    recommendations = RecommendationEngine().generate(report)

    assert recommendations == [
        "Add a README.md containing "
        "project purpose, installation, "
        "usage, and examples.",
        "Add a .gitignore file for "
        "virtual environments, caches, "
        "build artifacts, and secrets.",
    ]


def test_dirty_git_recommendation():
    report = clean_report()
    report.git.clean = False

    recommendations = RecommendationEngine().generate(report)

    assert recommendations == [
        "Review and commit or discard "
        "uncommitted Git changes."
    ]


def test_missing_remote_recommendation():
    report = clean_report()
    report.git.remote = False

    recommendations = RecommendationEngine().generate(report)

    assert recommendations == [
        "Configure a Git remote so the "
        "repository can be backed up "
        "and collaborated on."
    ]


def test_non_git_repository_has_no_git_recommendations():
    report = clean_report()
    report.git.is_repo = False
    report.git.clean = False
    report.git.remote = False

    recommendations = RecommendationEngine().generate(report)

    assert recommendations == []


def test_multiple_recommendations():
    report = clean_report()

    report.security_findings = [object()]
    report.complex_functions = [object()]
    report.large_functions = [object()]
    report.deep_functions = [object()]
    report.argument_heavy_functions = [object()]
    report.has_readme = False
    report.has_gitignore = False
    report.git.clean = False
    report.git.remote = False

    recommendations = RecommendationEngine().generate(report)

    assert len(recommendations) == 9


def test_ten_todos_do_not_trigger_warning_recommendation():
    report = clean_report()
    report.total_todos = 10

    assert RecommendationEngine().generate(report) == []


def test_git_recommendations_preserve_order():
    report = clean_report()
    report.git.clean = False
    report.git.remote = False

    recommendations = RecommendationEngine().generate(report)

    assert recommendations == [
        "Review and commit or discard "
        "uncommitted Git changes.",
        "Configure a Git remote so the "
        "repository can be backed up "
        "and collaborated on.",
    ]


def test_all_recommendation_categories_preserve_order():
    report = clean_report()

    report.security_findings = [object()]
    report.complex_functions = [object()]
    report.large_functions = [object()]
    report.deep_functions = [object()]
    report.argument_heavy_functions = [object()]
    report.has_readme = False
    report.has_gitignore = False
    report.git.clean = False
    report.git.remote = False

    recommendations = RecommendationEngine().generate(report)

    assert recommendations == [
        "Move hardcoded secrets to "
        "environment variables or a "
        "secret manager.",
        "Split high-complexity functions "
        "into smaller functions with "
        "single responsibilities.",
        "Break large functions into "
        "smaller logical units.",
        "Reduce deep nesting by using "
        "early returns and guard clauses.",
        "Reduce functions with many "
        "arguments by grouping related "
        "data into objects or dataclasses.",
        "Add a README.md containing "
        "project purpose, installation, "
        "usage, and examples.",
        "Add a .gitignore file for "
        "virtual environments, caches, "
        "build artifacts, and secrets.",
        "Review and commit or discard "
        "uncommitted Git changes.",
        "Configure a Git remote so the "
        "repository can be backed up "
        "and collaborated on.",
    ]
