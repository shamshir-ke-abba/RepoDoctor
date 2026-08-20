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
