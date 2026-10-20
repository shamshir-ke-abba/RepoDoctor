from repodoctor.models import RepositoryReport


class HealthScorer:
    """Calculate repository health scores."""

    def calculate(
        self,
        report: RepositoryReport,
    ) -> int:
        """Calculate the repository health score."""

        penalties = [
            self._security_penalty(report),
            self._code_quality_penalty(report),
            self._structure_penalty(report),
            self._git_penalty(report),
        ]

        score = 100 - sum(penalties)

        return max(
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

        if report.git.detached_head:
            penalty += 3

        if not report.git.upstream:
            penalty += 2

        if report.git.conflicts:
            penalty += min(
                report.git.conflicts * 5,
                15,
            )

        return penalty
