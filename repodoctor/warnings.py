class WarningEngine:
    """Generate repository health warnings."""

    def generate(self, report) -> list[str]:
        """Generate all warnings for a repository report."""

        warnings = []

        self._warn_security(report, warnings)
        self._warn_code_quality(report, warnings)
        self._warn_project_structure(report, warnings)
        self._warn_git(report, warnings)

        return warnings

    def _warn_security(
        self,
        report,
        warnings: list[str],
    ) -> None:
        """Generate security warnings."""

        if report.security_findings:
            warnings.append(
                f"{len(report.security_findings)} "
                "security finding(s)"
            )

    def _warn_code_quality(
        self,
        report,
        warnings: list[str],
    ) -> None:
        """Generate code-quality warnings."""

        if report.complex_functions:
            warnings.append(
                f"{len(report.complex_functions)} "
                "high-complexity function(s)"
            )

        if report.large_functions:
            warnings.append(
                f"{len(report.large_functions)} "
                "large function(s)"
            )

        if report.deep_functions:
            warnings.append(
                f"{len(report.deep_functions)} "
                "deeply nested function(s)"
            )

        if report.argument_heavy_functions:
            warnings.append(
                f"{len(report.argument_heavy_functions)} "
                "function(s) with too many arguments"
            )

        if report.large_files:
            warnings.append(
                f"{len(report.large_files)} "
                "large file(s)"
            )

        if report.total_todos > 10:
            warnings.append(
                f"{report.total_todos} "
                "TODO/FIXME comment(s)"
            )

    def _warn_project_structure(
        self,
        report,
        warnings: list[str],
    ) -> None:
        """Generate project-structure warnings."""

        if not report.has_readme:
            warnings.append("README is missing")

        if not report.has_gitignore:
            warnings.append(".gitignore is missing")

    def _warn_git(
        self,
        report,
        warnings: list[str],
    ) -> None:
        """Generate Git-health warnings."""

        if not report.git.is_repo:
            warnings.append(
                "Git repository is not configured"
            )
            return

        if not report.git.clean:
            warnings.append(
                "Git working tree has changes"
            )

        if report.git.conflicts:
            warnings.append(
                f"{report.git.conflicts} "
                "unresolved merge conflict(s)"
            )

        if report.git.detached_head:
            warnings.append(
                "Git HEAD is detached"
            )

        if not report.git.remote:
            warnings.append(
                "Git remote is not configured"
            )

        if not report.git.upstream:
            warnings.append(
                "Current branch has no upstream"
            )
