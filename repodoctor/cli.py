import argparse
from pathlib import Path

from repodoctor.reporting.json import JSONReporter
from repodoctor.reporting.terminal import TerminalReporter
from repodoctor.scanner import RepositoryScanner


def main():

    parser = argparse.ArgumentParser(
        prog="repodoctor",
        description=(
            "Analyze a repository and detect "
            "potential problems."
        ),
    )

    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Repository path to analyze",
    )

    parser.add_argument(
        "--format",
        choices=["terminal", "json"],
        default="terminal",
        help="Output format",
    )

    parser.add_argument(
        "--fail-under",
        type=int,
        metavar="SCORE",
        help=(
            "Exit with failure if the health "
            "score is below SCORE"
        ),
    )

    args = parser.parse_args()

    if args.fail_under is not None:
        if not 0 <= args.fail_under <= 100:
            parser.error(
                "--fail-under must be between 0 and 100"
            )

    root = Path(args.path)

    if not root.exists():
        parser.error(
            f"Path does not exist: {root}"
        )

    if not root.is_dir():
        parser.error(
            f"Path is not a directory: {root}"
        )

    scanner = RepositoryScanner(root)
    report = scanner.scan()

    if args.format == "json":
        reporter = JSONReporter()
    else:
        reporter = TerminalReporter()

    reporter.print_report(report)

    if args.fail_under is not None:

        if report.health_score < args.fail_under:

            print(
                f"\nFAIL: health score "
                f"{report.health_score}/100 is below "
                f"required threshold "
                f"{args.fail_under}/100"
            )

            raise SystemExit(1)

        print(
            f"\nPASS: health score "
            f"{report.health_score}/100 meets "
            f"required threshold "
            f"{args.fail_under}/100"
        )


if __name__ == "__main__":
    main()
