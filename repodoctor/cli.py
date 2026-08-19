import argparse
from pathlib import Path

from repodoctor.reporting.json import JSONReporter
from repodoctor.reporting.terminal import TerminalReporter
from repodoctor.scanner import RepositoryScanner


def build_parser():
    """Build and return the command-line argument parser."""

    parser = argparse.ArgumentParser(
        prog="repodoctor",
        description="Analyze a repository and detect potential problems.",
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
        default=None,
        metavar="SCORE",
        help="Exit with failure if the health score is below SCORE",
    )

    return parser


def validate_args(args):
    """Validate command-line arguments and return the repository path."""

    if args.fail_under is not None:
        if not 0 <= args.fail_under <= 100:
            print(
                "repodoctor: error: "
                "--fail-under must be between 0 and 100"
            )
            raise SystemExit(2)

    path = Path(args.path).expanduser()

    if not path.exists():
        print(
            f"repodoctor: error: Path does not exist: {path}"
        )
        raise SystemExit(2)

    if not path.is_dir():
        print(
            f"repodoctor: error: Path is not a directory: {path}"
        )
        raise SystemExit(2)

    return path.resolve()


def print_report(report, output_format):
    """Render the report using the requested output format."""

    if output_format == "json":
        JSONReporter().print_report(report)
    else:
        TerminalReporter().print_report(report)


def handle_threshold(report, fail_under):
    """Handle --fail-under and exit with the appropriate status."""

    if fail_under is None:
        return

    if report.health_score < fail_under:
        print(
            f"\nFAIL: health score {report.health_score}/100 "
            f"is below required threshold {fail_under}/100"
        )
        raise SystemExit(1)

    print(
        f"\nPASS: health score {report.health_score}/100 "
        f"meets required threshold {fail_under}/100"
    )


def main():
    """Run RepoDoctor from the command line."""

    parser = build_parser()
    args = parser.parse_args()

    path = validate_args(args)

    scanner = RepositoryScanner(path)
    report = scanner.scan()

    print_report(
        report,
        args.format,
    )

    handle_threshold(
        report,
        args.fail_under,
    )


if __name__ == "__main__":
    main()
