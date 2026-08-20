import re
from dataclasses import dataclass
from pathlib import Path

from repodoctor.file_collector import FileCollector


@dataclass
class SecurityFinding:
    file: str
    line: int
    rule: str
    severity: str
    message: str


class SecurityAnalyzer:
    """Scan source files for potentially sensitive information."""

    SECRET_PATTERNS = [
        (
            re.compile(
                r"(api[_-]?key|secret[_-]?key|access[_-]?token)"
                r"\s*=\s*['\"][^'\"]{8,}['\"]",
                re.IGNORECASE,
            ),
            "Potential hardcoded API key or token",
            "HIGH",
        ),
        (
            re.compile(
                r"(password|passwd|pwd)"
                r"\s*=\s*['\"][^'\"]+['\"]",
                re.IGNORECASE,
            ),
            "Potential hardcoded password",
            "HIGH",
        ),
        (
            re.compile(
                r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"
            ),
            "Private key detected",
            "CRITICAL",
        ),
        (
            re.compile(
                r"AKIA[0-9A-Z]{16}"
            ),
            "Possible AWS access key",
            "CRITICAL",
        ),
        (
            re.compile(
                r"gh[pousr]_[A-Za-z0-9_]{20,}"
            ),
            "Possible GitHub token",
            "CRITICAL",
        ),
    ]

    PLACEHOLDER_VALUES = {
        "changeme",
        "change_me",
        "change-me",
        "example",
        "example_key",
        "example_secret",
        "fake",
        "fake_key",
        "fake_secret",
        "dummy",
        "dummy_key",
        "dummy_secret",
        "placeholder",
        "placeholder_key",
        "placeholder_secret",
        "test",
        "test_key",
        "test_secret",
        "your_api_key",
        "your_secret_key",
        "your_token",
        "your_password",
    }

    SUSPICIOUS_FILES = {
        ".env",
        ".env.local",
        ".env.production",
        "credentials.json",
        "credentials.yaml",
        "credentials.yml",
        "secrets.json",
        "secrets.yaml",
        "secrets.yml",
    }

    def scan(
        self,
        collector: FileCollector | Path,
    ) -> list[SecurityFinding]:
        if isinstance(collector, Path):
            collector = FileCollector(collector)

        findings = []

        for path in collector.files():

            if path.name in self.SUSPICIOUS_FILES:

                findings.append(
                    SecurityFinding(
                        file=str(path),
                        line=1,
                        rule="SUSPICIOUS_FILE",
                        severity="HIGH",
                        message=(
                            "Potentially sensitive "
                            "configuration file"
                        ),
                    )
                )

            findings.extend(
                self._scan_file(path)
            )

        return findings

    def _scan_file(
        self,
        path: Path,
    ) -> list[SecurityFinding]:

        findings = []

        try:
            text = path.read_text(
                encoding="utf-8",
                errors="ignore",
            )
        except OSError:
            return findings

        for line_number, line in enumerate(
            text.splitlines(),
            start=1,
        ):

            if self._is_placeholder(line):
                continue

            for (
                pattern,
                message,
                severity,
            ) in self.SECRET_PATTERNS:

                if pattern.search(line):

                    findings.append(
                        SecurityFinding(
                            file=str(path),
                            line=line_number,
                            rule=pattern.pattern,
                            severity=severity,
                            message=message,
                        )
                    )

        return findings

    def _is_placeholder(self, line: str) -> bool:
        """Return True when a secret assignment uses an obvious placeholder."""

        match = re.search(
            r"=\s*['\"]([^'\"]+)['\"]",
            line,
        )

        if not match:
            return False

        value = match.group(1).strip().lower()

        if value in self.PLACEHOLDER_VALUES:
            return True

        placeholder_patterns = (
            r"^your[_-].*",
            r"^your\s+.*",
            r"^example[_-].*",
            r"^test[_-].*",
            r"^dummy[_-].*",
            r"^fake[_-].*",
            r"^placeholder[_-].*",
        )

        return any(
            re.match(pattern, value)
            for pattern in placeholder_patterns
        )
