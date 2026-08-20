from pathlib import Path
from repodoctor.file_collector import FileCollector

from repodoctor.analyzers.git import GitAnalyzer
from repodoctor.analyzers.python import PythonAnalyzer
from repodoctor.analyzers.security import SecurityAnalyzer
from repodoctor.analyzers.structure import StructureAnalyzer
from repodoctor.config import ScanConfig
from repodoctor.models import RepositoryReport
from repodoctor.recommendations import RecommendationEngine


class RepositoryScanner:
    """Scan a repository and build a complete health report."""

    def __init__(
        self,
        root: Path,
        config: ScanConfig | None = None,
    ):
        self.root = root.resolve()

        # Load configuration from pyproject.toml unless
        # an explicit configuration object was provided.
        self.config = (
            config
            if config is not None
            else ScanConfig.from_pyproject(self.root)
        )

        self.file_collector = FileCollector(
            self.root,
            max_file_size_bytes=self.config.max_file_size_bytes,
        )

        self.python_analyzer = PythonAnalyzer()
        self.security_analyzer = SecurityAnalyzer()
        self.structure_analyzer = StructureAnalyzer()
        self.git_analyzer = GitAnalyzer()
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

        self._generate_warnings(report)
        self._calculate_score(report)

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
                self.root
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

    # ------------------------------------------------------------------
    # Warnings
    # ------------------------------------------------------------------

    def _generate_warnings(
        self,
        report: RepositoryReport,
    ):
        """Generate all warnings for the repository."""

        self._warn_security(report)
        self._warn_code_quality(report)
        self._warn_project_structure(report)
        self._warn_git(report)

    def _warn_security(
        self,
        report: RepositoryReport,
    ):
        """Generate security warnings."""

        if report.security_findings:
            report.warnings.append(
                f"{len(report.security_findings)} "
                "security finding(s)"
            )

    def _warn_code_quality(
        self,
        report: RepositoryReport,
    ):
        """Generate code-quality warnings."""

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
        """Generate project-structure warnings."""

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
        """Generate Git health warnings."""

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

    # ------------------------------------------------------------------
    # Health score
    # ------------------------------------------------------------------

    def _calculate_score(
        self,
        report: RepositoryReport,
    ):
        """Calculate the repository health score."""

        penalties = [
            self._security_penalty(report),
            self._code_quality_penalty(report),
            self._structure_penalty(report),
            self._git_penalty(report),
        ]

        score = 100 - sum(penalties)

        report.health_score = max(
            0,
            min(100, score),
        )

    def _security_penalty(
        self,
        report: RepositoryReport,
    ) -> int:
        """Calculate security-related score penalty."""

        return len(
            report.security_findings
        ) * 8

    def _code_quality_penalty(
        self,
        report: RepositoryReport,
    ) -> int:
        """Calculate code-quality score penalty."""

        penalty = 0

        penalty += (
            len(report.complex_functions)
            * 3
        )

        penalty += (
            len(report.large_functions)
            * 2
        )

        penalty += (
            len(report.deep_functions)
            * 2
        )

        penalty += (
            len(
                report.argument_heavy_functions
            )
            * 2
        )

        penalty += (
            len(report.large_files)
            * 3
        )

        if report.total_todos > 10:
            penalty += 5

        return penalty

    def _structure_penalty(
        self,
        report: RepositoryReport,
    ) -> int:
        """Calculate project-structure score penalty."""

        penalty = 0

        if not report.has_readme:
            penalty += 10

        if not report.has_gitignore:
            penalty += 5

        return penalty

    def _git_penalty(
        self,
        report: RepositoryReport,
    ) -> int:
        """Calculate Git-health score penalty."""

        if not report.git.is_repo:
            return 5

        penalty = 0

        if not report.git.clean:
            penalty += 3

        if not report.git.remote:
            penalty += 3

        return penalty
