from repodoctor.models import RepositoryReport


class RecommendationEngine:
    """Generate actionable recommendations."""

    def generate(
        self,
        report: RepositoryReport,
    ) -> list[str]:

        recommendations = []

        self._security(
            report,
            recommendations,
        )

        self._complexity(
            report,
            recommendations,
        )

        self._function_size(
            report,
            recommendations,
        )

        self._nesting(
            report,
            recommendations,
        )

        self._arguments(
            report,
            recommendations,
        )

        self._documentation(
            report,
            recommendations,
        )

        self._git(
            report,
            recommendations,
        )

        return recommendations

    def _security(
        self,
        report: RepositoryReport,
        recommendations: list[str],
    ):

        if report.security_findings:

            recommendations.append(
                "Move hardcoded secrets to "
                "environment variables or a "
                "secret manager."
            )

    def _complexity(
        self,
        report: RepositoryReport,
        recommendations: list[str],
    ):

        if report.complex_functions:

            recommendations.append(
                "Split high-complexity functions "
                "into smaller functions with "
                "single responsibilities."
            )

    def _function_size(
        self,
        report: RepositoryReport,
        recommendations: list[str],
    ):

        if report.large_functions:

            recommendations.append(
                "Break large functions into "
                "smaller logical units."
            )

    def _nesting(
        self,
        report: RepositoryReport,
        recommendations: list[str],
    ):

        if report.deep_functions:

            recommendations.append(
                "Reduce deep nesting by using "
                "early returns and guard clauses."
            )

    def _arguments(
        self,
        report: RepositoryReport,
        recommendations: list[str],
    ):

        if report.argument_heavy_functions:

            recommendations.append(
                "Reduce functions with many "
                "arguments by grouping related "
                "data into objects or dataclasses."
            )

    def _documentation(
        self,
        report: RepositoryReport,
        recommendations: list[str],
    ):

        if not report.has_readme:

            recommendations.append(
                "Add a README.md containing "
                "project purpose, installation, "
                "usage, and examples."
            )

        if not report.has_gitignore:

            recommendations.append(
                "Add a .gitignore file for "
                "virtual environments, caches, "
                "build artifacts, and secrets."
            )

    def _git(
        self,
        report: RepositoryReport,
        recommendations: list[str],
    ):

        if not report.git.is_repo:
            return

        if not report.git.clean:

            recommendations.append(
                "Review and commit or discard "
                "uncommitted Git changes."
            )

        if not report.git.remote:

            recommendations.append(
                "Configure a Git remote so the "
                "repository can be backed up "
                "and collaborated on."
            )
