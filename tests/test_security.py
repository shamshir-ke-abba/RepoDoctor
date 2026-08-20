from pathlib import Path

from repodoctor.analyzers.security import SecurityAnalyzer
from repodoctor.file_collector import FileCollector


def test_detects_fake_api_key(tmp_path: Path):
    source = """
API_KEY = "this_is_a_fake_api_key_123456"
"""

    file = tmp_path / "config.py"
    file.write_text(source)

    findings = SecurityAnalyzer().scan(tmp_path)

    assert len(findings) >= 1
    assert any(
        "API key" in finding.message
        or "token" in finding.message
        for finding in findings
    )


def test_clean_file_has_no_security_findings(
    tmp_path: Path,
):
    source = """
def hello():
    return "hello"
"""

    file = tmp_path / "clean.py"
    file.write_text(source)

    findings = SecurityAnalyzer().scan(tmp_path)

    assert findings == []


def test_ignores_placeholder_api_key(tmp_path: Path):
    source = """
API_KEY = "your_api_key_here"
"""

    file = tmp_path / "config.py"
    file.write_text(source)

    findings = SecurityAnalyzer().scan(tmp_path)

    assert findings == []


def test_ignores_environment_variable_secret(tmp_path: Path):
    source = """
import os

API_KEY = os.getenv("API_KEY")
PASSWORD = os.environ["PASSWORD"]
"""

    file = tmp_path / "config.py"
    file.write_text(source)

    findings = SecurityAnalyzer().scan(tmp_path)

    assert findings == []


def test_detects_hardcoded_password(tmp_path: Path):
    source = """
PASSWORD = "super_secret_password_123"
"""

    file = tmp_path / "config.py"
    file.write_text(source)

    findings = SecurityAnalyzer().scan(tmp_path)

    assert any(
        finding.severity == "HIGH"
        and "password" in finding.message.lower()
        for finding in findings
    )


def test_ignores_test_secret_placeholder(tmp_path: Path):
    source = """
SECRET_KEY = "test_secret_key"
API_KEY = "changeme"
"""

    file = tmp_path / "config.py"
    file.write_text(source)

    findings = SecurityAnalyzer().scan(tmp_path)

    assert findings == []


def test_detects_aws_access_key(tmp_path: Path):
    source = """
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
"""

    file = tmp_path / "config.py"
    file.write_text(source)

    findings = SecurityAnalyzer().scan(tmp_path)

    assert any(
        finding.severity == "CRITICAL"
        and "AWS" in finding.message
        for finding in findings
    )


def test_detects_github_token(tmp_path: Path):
    source = """
GITHUB_TOKEN = "ghp_abcdefghijklmnopqrstuvwxyz123456"
"""

    file = tmp_path / "config.py"
    file.write_text(source)

    findings = SecurityAnalyzer().scan(tmp_path)

    assert any(
        finding.severity == "CRITICAL"
        and "GitHub" in finding.message
        for finding in findings
    )


def test_detects_private_key(tmp_path: Path):
    source = """
-----BEGIN RSA PRIVATE KEY-----
example-private-key-data
-----END RSA PRIVATE KEY-----
"""

    file = tmp_path / "private.pem"
    file.write_text(source)

    findings = SecurityAnalyzer().scan(tmp_path)

    assert any(
        finding.severity == "CRITICAL"
        and "Private key" in finding.message
        for finding in findings
    )


def test_detects_suspicious_env_file(tmp_path: Path):
    file = tmp_path / ".env"
    file.write_text("DATABASE_URL=example")

    findings = SecurityAnalyzer().scan(tmp_path)

    assert any(
        finding.rule == "SUSPICIOUS_FILE"
        and finding.severity == "HIGH"
        for finding in findings
    )


def test_reports_multiple_security_findings(tmp_path: Path):
    source = """
API_KEY = "real_api_key_12345678"
PASSWORD = "super_secret_password"
"""

    file = tmp_path / "config.py"
    file.write_text(source)

    findings = SecurityAnalyzer().scan(tmp_path)

    assert len(findings) == 2


def test_scan_uses_configured_file_collector(
    tmp_path: Path,
):
    file = tmp_path / "large.py"
    file.write_text(
        'API_KEY = "this_is_a_fake_api_key_123456"\n'
        + "x" * 100
    )

    collector = FileCollector(
        tmp_path,
        max_file_size_bytes=10,
    )

    findings = SecurityAnalyzer().scan(collector)

    assert findings == []


def test_detects_all_suspicious_file_names(tmp_path: Path):
    suspicious_names = [
        ".env",
        ".env.local",
        ".env.production",
        "credentials.json",
        "credentials.yaml",
        "credentials.yml",
        "secrets.json",
        "secrets.yaml",
        "secrets.yml",
    ]

    for name in suspicious_names:
        file = tmp_path / name
        file.write_text("VALUE=example")

    findings = SecurityAnalyzer().scan(tmp_path)

    suspicious_findings = [
        finding
        for finding in findings
        if finding.rule == "SUSPICIOUS_FILE"
    ]

    assert len(suspicious_findings) == len(
        suspicious_names
    )


def test_suspicious_file_and_secret_are_both_reported(
    tmp_path: Path,
):
    file = tmp_path / ".env"
    file.write_text(
        'API_KEY = "real_api_key_12345678"\n'
    )

    findings = SecurityAnalyzer().scan(tmp_path)

    assert len(findings) == 2
    assert any(
        finding.rule == "SUSPICIOUS_FILE"
        for finding in findings
    )
    assert any(
        "API key" in finding.message
        for finding in findings
    )


def test_security_finding_contains_exact_location_and_details(
    tmp_path: Path,
):
    source = """
# harmless
API_KEY = "this_is_a_real_secret_value"
"""

    file = tmp_path / "config.py"
    file.write_text(source)

    findings = SecurityAnalyzer().scan(tmp_path)

    finding = next(
        finding
        for finding in findings
        if "API key" in finding.message
    )

    assert finding.file == str(file)
    assert finding.line == 3
    assert finding.severity == "HIGH"
    assert finding.rule == (
        r"(api[_-]?key|secret[_-]?key|access[_-]?token)"
        r"\s*=\s*['\"][^'\"]{8,}['\"]"
    )
    assert finding.message == (
        "Potential hardcoded API key or token"
    )


def test_detects_secret_key_and_access_token_variants(
    tmp_path: Path,
):
    source = """
secret-key = "abcdefgh123456"
access_token = "abcdefgh123456"
"""

    file = tmp_path / "config.py"
    file.write_text(source)

    findings = SecurityAnalyzer().scan(tmp_path)

    assert len(findings) == 2
    assert all(
        finding.severity == "HIGH"
        for finding in findings
    )


def test_detects_password_variable_variants(tmp_path: Path):
    source = """
passwd = "secret123"
pwd = "secret456"
"""

    file = tmp_path / "config.py"
    file.write_text(source)

    findings = SecurityAnalyzer().scan(tmp_path)

    assert len(findings) == 2
    assert all(
        "password" in finding.message.lower()
        for finding in findings
    )


def test_short_api_key_is_not_reported(tmp_path: Path):
    source = """
API_KEY = "short"
"""

    file = tmp_path / "config.py"
    file.write_text(source)

    findings = SecurityAnalyzer().scan(tmp_path)

    assert findings == []


def test_secret_pattern_requires_assignment(tmp_path: Path):
    source = """
print("API_KEY = \\"this_is_long_enough_secret\\"")
"""

    file = tmp_path / "config.py"
    file.write_text(source)

    findings = SecurityAnalyzer().scan(tmp_path)

    assert findings == []


def test_placeholder_patterns_are_ignored(tmp_path: Path):
    values = [
        "your_api_key",
        "your-secret",
        "your secret",
        "example_key_value",
        "test-secret",
        "dummy_value",
        "fake-value",
        "placeholder_value",
    ]

    source = "\n".join(
        f'API_KEY = "{value}"'
        for value in values
    )

    file = tmp_path / "config.py"
    file.write_text(source)

    findings = SecurityAnalyzer().scan(tmp_path)

    assert findings == []


def test_placeholder_values_are_case_insensitive(
    tmp_path: Path,
):
    source = """
API_KEY = "CHANGE_ME"
PASSWORD = "Dummy"
SECRET_KEY = "PLACEHOLDER"
"""

    file = tmp_path / "config.py"
    file.write_text(source)

    findings = SecurityAnalyzer().scan(tmp_path)

    assert findings == []


def test_non_assignment_line_is_not_placeholder(
    tmp_path: Path,
):
    source = """
print("your_api_key")
"""

    file = tmp_path / "config.py"
    file.write_text(source)

    findings = SecurityAnalyzer().scan(tmp_path)

    assert findings == []


def test_scan_accepts_path_directly(tmp_path: Path):
    file = tmp_path / "config.py"
    file.write_text(
        'API_KEY = "this_is_a_real_secret"\n'
    )

    findings = SecurityAnalyzer().scan(file.parent)

    assert len(findings) == 1


def test_empty_file_has_no_findings(tmp_path: Path):
    file = tmp_path / "empty.py"
    file.write_text("")

    findings = SecurityAnalyzer().scan(tmp_path)

    assert findings == []


def test_multiple_findings_report_correct_line_numbers(
    tmp_path: Path,
):
    source = """
API_KEY = "first_real_secret_123"
print("hello")
PASSWORD = "second_real_secret"
"""

    file = tmp_path / "config.py"
    file.write_text(source)

    findings = SecurityAnalyzer().scan(tmp_path)

    assert [finding.line for finding in findings] == [2, 4]


def test_scan_file_returns_empty_when_file_cannot_be_read(
    tmp_path: Path,
    monkeypatch,
):
    analyzer = SecurityAnalyzer()
    file = tmp_path / "unreadable.py"
    file.write_text("API_KEY = 'secret_value_12345'")

    def raise_os_error(*args, **kwargs):
        raise OSError("permission denied")

    monkeypatch.setattr(
        Path,
        "read_text",
        raise_os_error,
    )

    findings = analyzer._scan_file(file)

    assert findings == []
