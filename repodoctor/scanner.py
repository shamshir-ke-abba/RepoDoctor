from repodoctor.recommendations import RecommendationEngine
from pathlib import Path

from repodoctor.analyzers.git import GitAnalyzer
from repodoctor.analyzers.python import PythonAnalyzer
from repodoctor.analyzers.security import SecurityAnalyzer
from repodoctor.analyzers.structure import StructureAnalyzer
from repodoctor.models import RepositoryReport


COMPLEXITY_THRESHOLD = 10
LARGE_FILE_THRESHOLD = 500
LARGE_FUNCTION_THRESHOLD = 50
NESTING_THRESHOLD = 4
ARGUMENT_THRESHOLD = 6


class RepositoryScanner:
    """Scan a repository and build a complete report."""

    def __init__(self, root: Path):
        self.root = root.resolve()

        self.python_analyzer = PythonAnalyzer()
        self.security_analyzer = SecurityAnalyzer()
        self.structure_analyzer = StructureAnalyzer()
        self.git_analyzer = GitAnalyzer()
        self.recommendation_engine = (
            RecommendationEngine()
        )
    def scan(self) -> RepositoryReport:

        report = RepositoryReport(
            path=str(self.root)
        )

        self._scan_python(report)
        self._scan_structure(report)
        self._scan_security(report)
        self._scan_git(report)

        self._generate_warnings(report)
        self._calculate_score(report)
        report.recommendations = (
            self.recommendation_engine.generate(
                report
            )
        )


        return report

    def _scan_python(
        self,
        report: RepositoryReport,
    ):

        for path in self._python_files():

            result = self.python_analyzer.analyze(path)

            self._update_project_stats(
                report,
                result,
            )

            self._check_file_size(
                report,
                result,
            )

            self._check_functions(
                report,
                result,
            )

    def _update_project_stats(
        self,
        report: RepositoryReport,
        result,
    ):

        report.python_files += 1
        report.total_lines += result.lines
        report.total_functions += result.functions
        report.total_classes += result.classes
        report.total_todos += result.todos

    def _check_file_size(
        self,
        report: RepositoryReport,
        result,
    ):

        if result.lines >= LARGE_FILE_THRESHOLD:

            report.large_files.append(
                f"{result.path} ({result.lines} lines)"
            )

    def _check_functions(
        self,
        report: RepositoryReport,
        result,
    ):

        for function in result.functions_report:

            if function.lines >= LARGE_FUNCTION_THRESHOLD:
                report.large_functions.append(
                    function
                )

            if function.nesting_depth >= NESTING_THRESHOLD:
                report.deep_functions.append(
                    function
                )

            if function.arguments >= ARGUMENT_THRESHOLD:
                report.argument_heavy_functions.append(
                    function
                )

            if function.complexity >= COMPLEXITY_THRESHOLD:
                report.complex_functions.append(
                    function
                )

    def _scan_structure(
        self,
        report: RepositoryReport,
    ):

        result = self.structure_analyzer.analyze(
            self.root
        )

        report.has_readme = result["has_readme"]
        report.has_gitignore = result["has_gitignore"]

    def _scan_security(
        self,
        report: RepositoryReport,
    ):

        report.security_findings = (
            self.security_analyzer.scan(
                self.root
            )
        )

    def _scan_git(
        self,
        report: RepositoryReport,
    ):

        report.git = self.git_analyzer.analyze(
            self.root
        )

        report.is_git_repo = report.git.is_repo

    def _python_files(self):

        ignored = {
            ".git",
            ".venv",
            "venv",
            "__pycache__",
            "node_modules",
            ".mypy_cache",
            ".pytest_cache",
        }

        for path in self.root.rglob("*.py"):

            if any(
                part in ignored
                for part in path.parts
            ):
                continue

            yield path

    def _generate_warnings(
        self,
        report: RepositoryReport,
    ):

        self._warn_security(report)
        self._warn_code_quality(report)
        self._warn_project_structure(report)
        self._warn_git(report)

    def _warn_security(
        self,
        report: RepositoryReport,
    ):

        if report.security_findings:

            report.warnings.append(
                f"{len(report.security_findings)} "
                "security finding(s)"
            )

    def _warn_code_quality(
        self,
        report: RepositoryReport,
    ):

        warning_groups = [
            (
                len(report.complex_functions),
                "high-complexity function(s)",
            ),
            (
                len(report.large_functions),
                "large function(s)",
            ),
            (
                len(report.deep_functions),
                "deeply nested function(s)",
            ),
            (
                len(report.argument_heavy_functions),
                "function(s) with too many arguments",
            ),
            (
                len(report.large_files),
                "large Python file(s)",
            ),
        ]

        for count, message in warning_groups:

            if count:
                report.warnings.append(
                    f"{count} {message}"
                )

        if report.total_todos:

            report.warnings.append(
                f"{report.total_todos} "
                "TODO/FIXME comment(s)"
            )

    def _warn_project_structure(
        self,
        report: RepositoryReport,
    ):

        if not report.has_readme:

            report.warnings.append(
                "README file is missing"
            )

        if not report.has_gitignore:

            report.warnings.append(
                ".gitignore is missing"
            )

    def _warn_git(
        self,
        report: RepositoryReport,
    ):

        if not report.git.is_repo:
            return

        if not report.git.clean:

            report.warnings.append(
                "Git working tree has changes"
            )

        if not report.git.remote:

            report.warnings.append(
                "Git remote is not configured"
            )

    def _calculate_score(
        self,
        report: RepositoryReport,
    ):

        score = 100

        score -= (
            len(report.security_findings) * 8
        )

        score -= (
            len(report.complex_functions) * 3
        )

        score -= (
            len(report.large_functions) * 2
        )

        score -= (
            len(report.deep_functions) * 2
        )

        score -= (
            len(report.argument_heavy_functions) * 2
        )

        score -= (
            len(report.large_files) * 3
        )

        if report.total_todos > 10:
            score -= 5

        if not report.has_readme:
            score -= 10

        if not report.has_gitignore:
            score -= 5

        if report.git.is_repo:

            if not report.git.clean:
                score -= 3

            if not report.git.remote:
                score -= 3

        else:

            score -= 5

        report.health_score = max(
            0,
            min(100, score),
        )
