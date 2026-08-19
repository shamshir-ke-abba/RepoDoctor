from pathlib import Path

from repodoctor.analyzers.security import SecurityAnalyzer


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
