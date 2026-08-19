import json
from dataclasses import asdict

from repodoctor.models import RepositoryReport


class JSONReporter:
    """Render a repository report as JSON."""

    def print_report(
        self,
        report: RepositoryReport,
    ):

        data = asdict(report)

        print(
            json.dumps(
                data,
                indent=2,
                default=str,
            )
        )
