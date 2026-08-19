from pathlib import Path

from repodoctor.analyzers.python import PythonAnalyzer
from repodoctor.analyzers.structure import StructureAnalyzer
from repodoctor.models import RepositoryReport


class RepositoryScanner:
    """Scan a repository and build a complete report."""

    def __init__(self, root: Path):
        self.root = root.resolve()

        self.python_analyzer = PythonAnalyzer()
        self.structure_analyzer = StructureAnalyzer()

    def scan(self) -> RepositoryReport:
        report = RepositoryReport(
            path=str(self.root)
        )

        self._scan_python(report)
        self._scan_structure(report)
        self._generate_warnings(report)
        self._calculate_score(report)

        return report

    def _scan_python(self, report: RepositoryReport):
        for path in self._python_files():
            result = self.python_analyzer.analyze(path)

            report.python_files += 1
            report.total_lines += result.lines
            report.total_functions += result.functions
            report.total_classes += result.classes
            report.total_todos += result.todos

            if result.lines > 500:
                report.large_files.append(
                    f"{result.path} ({result.lines} lines)"
                )

            if result.complexity >= 10:
                report.complex_functions.append(
                    f"{result.path} (complexity {result.complexity})"
                )

    def _scan_structure(self, report: RepositoryReport):
        result = self.structure_analyzer.analyze(self.root)

        report.has_readme = result["has_readme"]
        report.has_gitignore = result["has_gitignore"]
        report.is_git_repo = result["is_git_repo"]

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
            if any(part in ignored for part in path.parts):
                continue

            yield path

    def _generate_warnings(self, report: RepositoryReport):

        if report.large_files:
            report.warnings.append(
                f"{len(report.large_files)} large Python file(s)"
            )

        if report.complex_functions:
            report.warnings.append(
                f"{len(report.complex_functions)} "
                "high-complexity file(s)"
            )

        if report.total_todos:
            report.warnings.append(
                f"{report.total_todos} TODO/FIXME comment(s)"
            )

        if not report.has_readme:
            report.warnings.append(
                "README file is missing"
            )

        if not report.has_gitignore:
            report.warnings.append(
                ".gitignore is missing"
            )

        if not report.is_git_repo:
            report.warnings.append(
                "Not a Git repository"
            )

    def _calculate_score(self, report: RepositoryReport):

        score = 100

        score -= len(report.large_files) * 3
        score -= len(report.complex_functions) * 3

        if report.total_todos > 10:
            score -= 5

        if not report.has_readme:
            score -= 10

        if not report.has_gitignore:
            score -= 5

        if not report.is_git_repo:
            score -= 5

        report.health_score = max(
            0,
            min(100, score)
        )
