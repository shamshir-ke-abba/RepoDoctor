import argparse
from pathlib import Path

from repodoctor.reporting.terminal import TerminalReporter
from repodoctor.scanner import RepositoryScanner


def main():

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

    args = parser.parse_args()

    root = Path(args.path)

    if not root.exists():
        parser.error(f"Path does not exist: {root}")

    if not root.is_dir():
        parser.error(f"Path is not a directory: {root}")

    scanner = RepositoryScanner(root)
    report = scanner.scan()

    reporter = TerminalReporter()
    reporter.print_report(report)


if __name__ == "__main__":
    main()
