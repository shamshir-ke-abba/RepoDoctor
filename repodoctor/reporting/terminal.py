from repodoctor.models import RepositoryReport


class TerminalReporter:

    def print_report(self, report: RepositoryReport):

        print()
        print("╭──────────────────────────────────────╮")
        print("│              REPO DOCTOR             │")
        print("│       Repository Health Report       │")
        print("╰──────────────────────────────────────╯")

        print()
        print(f"Repository: {report.path}")

        self._section("PROJECT")

        print(f"Python files       {report.python_files}")
        print(f"Total lines        {report.total_lines}")
        print(f"Functions          {report.total_functions}")
        print(f"Classes            {report.total_classes}")
        print(f"TODO/FIXME         {report.total_todos}")

        self._section("STRUCTURE")

        self._status("README", report.has_readme)
        self._status(".gitignore", report.has_gitignore)
        self._status("Git repository", report.is_git_repo)

        self._section("WARNINGS")

        if report.warnings:
            for warning in report.warnings:
                print(f"⚠ {warning}")
        else:
            print("✓ No warnings detected")

        self._section("LARGE FILES")

        if report.large_files:
            for item in report.large_files:
                print(f"⚠ {item}")
        else:
            print("✓ No unusually large files")

        self._section("COMPLEXITY")

        if report.complex_functions:
            for item in report.complex_functions:
                print(f"⚠ {item}")
        else:
            print("✓ No highly complex files")

        print()
        print("──────────────────────────────────────")
        print(f"HEALTH SCORE: {report.health_score}/100")
        print("──────────────────────────────────────")
        print()

    def _section(self, name: str):
        print()
        print(name)
        print("─" * 38)

    def _status(self, name: str, success: bool):
        symbol = "✓" if success else "⚠"
        print(f"{symbol} {name}")
