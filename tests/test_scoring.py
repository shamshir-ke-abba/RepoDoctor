from repodoctor.models import RepositoryReport
from repodoctor.scoring import HealthScorer


def clean_report():
    report = RepositoryReport(path=".")

    report.has_readme = True
    report.has_gitignore = True
    report.git.is_repo = True
    report.git.clean = True
    report.git.remote = True

    return report


def test_clean_repository_has_perfect_score():
    report = clean_report()

    assert HealthScorer().calculate(report) == 100


def test_security_findings_reduce_score():
    report = clean_report()

    report.security_findings = [object(), object()]

    assert HealthScorer().calculate(report) == 84


def test_code_quality_penalties():
    report = clean_report()

    report.complex_functions = [object()]
    report.large_functions = [object(), object()]
    report.deep_functions = [object()]
    report.argument_heavy_functions = [object()]
    report.large_files = [object()]

    assert HealthScorer().calculate(report) == 86


def test_todos_over_threshold_reduce_score():
    report = clean_report()

    report.total_todos = 11

    assert HealthScorer().calculate(report) == 95


def test_missing_readme_reduces_score():
    report = clean_report()

    report.has_readme = False

    assert HealthScorer().calculate(report) == 90


def test_missing_gitignore_reduces_score():
    report = clean_report()

    report.has_gitignore = False

    assert HealthScorer().calculate(report) == 95


def test_git_penalties():
    report = clean_report()

    report.git.clean = False
    report.git.remote = False

    assert HealthScorer().calculate(report) == 94


def test_non_git_repository_penalty():
    report = clean_report()

    report.git.is_repo = False

    assert HealthScorer().calculate(report) == 95


def test_score_never_goes_below_zero():
    report = clean_report()

    report.security_findings = [object()] * 20

    assert HealthScorer().calculate(report) == 0


def test_score_never_goes_above_hundred():
    report = clean_report()

    assert HealthScorer().calculate(report) == 100
