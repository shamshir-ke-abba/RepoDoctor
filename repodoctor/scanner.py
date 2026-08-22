from pathlib import Path

from repodoctor.file_collector import FileCollector
from repodoctor.analyzers.git import GitAnalyzer
from repodoctor.analyzers.python import PythonAnalyzer
from repodoctor.analyzers.security import SecurityAnalyzer
from repodoctor.analyzers.structure import StructureAnalyzer
from repodoctor.config import ScanConfig
from repodoctor.models import RepositoryReport
from repodoctor.recommendations import RecommendationEngine
from repodoctor.scoring import HealthScorer
from repodoctor.warnings import WarningEngine


class RepositoryScanner:
    """Scan a repository and build a complete health report."""

    def __init__(
        self,
        root: Path,
        config: ScanConfig | None = None,
    ):
        self.root = root.resolve()

        self.config = (
            config
            if config is not None
            else ScanConfig.from_pyproject(self.root)
        )

        self.file_collector = FileCollector(
            self.root,
            max_file_size_bytes=self.config.max_file_size_bytes,
            excluded_directories=(
                self.config.excluded_directories
            ),
        )

        self.python_analyzer = PythonAnalyzer()
        self.security_analyzer = SecurityAnalyzer()
        self.structure_analyzer = StructureAnalyzer()
        self.git_analyzer = GitAnalyzer()
        self.warning_engine = WarningEngine()
        self.health_scorer = HealthScorer()
        self.recommendation_engine = RecommendationEngine()

    def scan(self) -> RepositoryReport:
        """Run all analyzers and build the final report."""

        report = RepositoryReport(
            path=str(self.root)
        )

        self._scan_python(report)
        self._scan_structure(report)
        self._scan_security(report)
        self._scan_git(report)

        report.warnings = (
            self.warning_engine.generate(report)
        )

        report.health_score = (
            self.health_scorer.calculate(report)
        )

        report.recommendations = (
            self.recommendation_engine.generate(report)
        )

        return report

    # ------------------------------------------------------------------
    # Python analysis
    # ------------------------------------------------------------------

    def _scan_python(
        self,
        report: RepositoryReport,
    ):
        """Analyze all Python files in the repository."""

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
        """Update repository-wide Python statistics."""

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
        """Record Python files exceeding the configured size threshold."""

        if (
            result.lines
            >= self.config.large_file_threshold
        ):
            report.large_files.append(
                f"{result.path} ({result.lines} lines)"
            )

    def _check_functions(
        self,
        report: RepositoryReport,
        result,
    ):
        """Classify functions according to configured thresholds."""

        for function in result.functions_report:
            self._check_function_size(
                report,
                function,
            )

            self._check_function_nesting(
                report,
                function,
            )

            self._check_function_arguments(
                report,
                function,
            )

            self._check_function_complexity(
                report,
                function,
            )

    def _check_function_size(
        self,
        report: RepositoryReport,
        function,
    ):
        """Check function length."""

        if (
            function.lines
            >= self.config.large_function_threshold
        ):
            report.large_functions.append(function)

    def _check_function_nesting(
        self,
        report: RepositoryReport,
        function,
    ):
        """Check function nesting depth."""

        if (
            function.nesting_depth
            >= self.config.nesting_threshold
        ):
            report.deep_functions.append(function)

    def _check_function_arguments(
        self,
        report: RepositoryReport,
        function,
    ):
        """Check number of function arguments."""

        if (
            function.arguments
            >= self.config.argument_threshold
        ):
            report.argument_heavy_functions.append(
                function
            )

    def _check_function_complexity(
        self,
        report: RepositoryReport,
        function,
    ):
        """Check cyclomatic-style complexity."""

        if (
            function.complexity
            >= self.config.complexity_threshold
        ):
            report.complex_functions.append(
                function
            )

    # ------------------------------------------------------------------
    # Repository analysis
    # ------------------------------------------------------------------

    def _scan_structure(
        self,
        report: RepositoryReport,
    ):
        """Analyze repository structure."""

        result = self.structure_analyzer.analyze(
            self.root
        )

        report.has_readme = result["has_readme"]
        report.has_gitignore = result[
            "has_gitignore"
        ]

    def _scan_security(
        self,
        report: RepositoryReport,
    ):
        """Scan the repository for security problems."""

        report.security_findings = (
            self.security_analyzer.scan(
                self.file_collector
            )
        )

    def _scan_git(
        self,
        report: RepositoryReport,
    ):
        """Analyze Git repository health."""

        report.git = self.git_analyzer.analyze(
            self.root
        )

        report.is_git_repo = report.git.is_repo

    def _python_files(self):
        """Yield eligible Python files."""

        yield from self.file_collector.python_files()
