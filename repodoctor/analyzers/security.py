import re
from dataclasses import dataclass
from pathlib import Path


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

    def scan(self, root: Path) -> list[SecurityFinding]:

        findings = []

        for path in self._files(root):

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

    def _files(self, root: Path):

        ignored = {
            ".git",
            ".venv",
            "venv",
            "__pycache__",
            "node_modules",
            ".mypy_cache",
            ".pytest_cache",
        }

        for path in root.rglob("*"):

            if not path.is_file():
                continue

            if any(
                part in ignored
                for part in path.parts
            ):
                continue

            # Skip very large files.
            try:
                if path.stat().st_size > 2_000_000:
                    continue
            except OSError:
                continue

            yield path
