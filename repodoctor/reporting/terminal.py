from repodoctor.models import RepositoryReport


class TerminalReporter:
    """Render repository health reports in the terminal."""

    def print_report(
        self,
        report: RepositoryReport,
    ):
        self._print_header(report)
        self._print_project(report)
        self._print_structure(report)
        self._print_git(report)
        self._print_warnings(report)
        self._print_large_files(report)
        self._print_complexity(report)
        self._print_function_size(report)
        self._print_nesting(report)
        self._print_arguments(report)
        self._print_security(report)
        self._print_recommendations(report)

    def _print_recommendations(
        self,
        report: RepositoryReport,
    ):
        self._section("RECOMMENDATIONS")

        if not report.recommendations:
            print("✓ No recommendations")
            return

        for recommendation in report.recommendations:
            print(f"→ {recommendation}")

        self._print_score(report)

    def _print_header(
        self,
        report: RepositoryReport,
    ):
        print()

        print(
            "╭──────────────────────────────────────╮"
        )
        print(
            "│              REPO DOCTOR             │"
        )
        print(
            "│       Repository Health Report       │"
        )
        print(
            "╰──────────────────────────────────────╯"
        )

        print()
        print(f"Repository: {report.path}")

    def _print_project(
        self,
        report: RepositoryReport,
    ):
        self._section("PROJECT")

        print(
            f"Python files       "
            f"{report.python_files}"
        )

        print(
            f"Total lines        "
            f"{report.total_lines}"
        )

        print(
            f"Functions          "
            f"{report.total_functions}"
        )

        print(
            f"Classes            "
            f"{report.total_classes}"
        )

        print(
            f"TODO/FIXME         "
            f"{report.total_todos}"
        )

    def _print_structure(
        self,
        report: RepositoryReport,
    ):
        self._section("STRUCTURE")

        self._status(
            "README",
            report.has_readme,
        )

        self._status(
            ".gitignore",
            report.has_gitignore,
        )

        self._status(
            "Git repository",
            report.is_git_repo,
        )

    def _print_git(
        self,
        report: RepositoryReport,
    ):
        self._section("GIT HEALTH")

        if not report.git.is_repo:
            print("⚠ Not a Git repository")
            return

        print(
            f"Branch             "
            f"{report.git.branch}"
        )

        print(
            f"Commits            "
            f"{report.git.commits}"
        )

        working_tree = (
            "CLEAN"
            if report.git.clean
            else "DIRTY"
        )

        print(
            f"Working tree       "
            f"{working_tree}"
        )

        print(
            f"Untracked files    "
            f"{report.git.untracked}"
        )

        print(
            f"Modified files     "
            f"{report.git.modified}"
        )

        remote = (
            "✓ configured"
            if report.git.remote
            else "⚠ not configured"
        )

        print(
            f"Remote             "
            f"{remote}"
        )

    def _print_warnings(
        self,
        report: RepositoryReport,
    ):
        self._section("WARNINGS")

        if not report.warnings:
            print("✓ No warnings detected")
            return

        for warning in report.warnings:
            print(f"⚠ {warning}")

    def _print_large_files(
        self,
        report: RepositoryReport,
    ):
        self._section("LARGE FILES")

        if not report.large_files:
            print(
                "✓ No unusually large files"
            )
            return

        for item in report.large_files:
            print(f"⚠ {item}")

    def _print_complexity(
        self,
        report: RepositoryReport,
    ):
        self._section("COMPLEXITY")

        if not report.complex_functions:
            print(
                "✓ No highly complex functions"
            )
            return

        for function in report.complex_functions:
            self._print_function(
                function,
                (
                    f"{function.name}() "
                    f"complexity: "
                    f"{function.complexity}"
                ),
            )

    def _print_function_size(
        self,
        report: RepositoryReport,
    ):
        self._section("FUNCTION SIZE")

        if not report.large_functions:
            print(
                "✓ No unusually large functions"
            )
            return

        for function in report.large_functions:
            lines = (
                function.end_line
                - function.line
                + 1
            )

            self._print_function(
                function,
                (
                    f"{function.name}() "
                    f"{lines} lines"
                ),
            )

    def _print_nesting(
        self,
        report: RepositoryReport,
    ):
        self._section("NESTING")

        if not report.deep_functions:
            print(
                "✓ No deeply nested functions"
            )
            return

        for function in report.deep_functions:
            self._print_function(
                function,
                (
                    f"{function.name}() "
                    f"nesting depth: "
                    f"{function.nesting_depth}"
                ),
            )

    def _print_arguments(
        self,
        report: RepositoryReport,
    ):
        self._section("ARGUMENTS")

        if not report.argument_heavy_functions:
            print(
                "✓ No functions with too many arguments"
            )
            return

        for function in report.argument_heavy_functions:
            self._print_function(
                function,
                (
                    f"{function.name}() "
                    f"{function.arguments} arguments"
                ),
            )

    def _print_security(
        self,
        report: RepositoryReport,
    ):
        self._section("SECURITY")

        if not report.security_findings:
            print(
                "✓ No obvious security issues detected"
            )
            return

        for finding in report.security_findings:
            print(
                f"⚠ [{finding.severity}] "
                f"{finding.file}:{finding.line} "
                f"{finding.rule}: "
                f"{finding.message}"
            )

    def _print_score(
        self,
        report: RepositoryReport,
    ):
        print()
        print("─" * 40)
        print(
            f"HEALTH SCORE: "
            f"{report.health_score}/100"
        )
        print("─" * 40)

    def _print_function(
        self,
        function,
        description: str,
    ):
        print(
            f"⚠ {function.file}:{function.line}"
        )
        print(
            f"  └── {description}"
        )

    def _section(
        self,
        title: str,
    ):
        print()
        print(title)
        print("─" * 40)

    def _status(
        self,
        name: str,
        status: bool,
    ):
        symbol = "✓" if status else "⚠"
        print(
            f"{symbol} {name}"
        )
