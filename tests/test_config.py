from pathlib import Path

from repodoctor.config import ScanConfig


def test_default_config():
    config = ScanConfig()

    assert config.complexity_threshold == 10
    assert config.large_file_threshold == 500
    assert config.large_function_threshold == 50
    assert config.nesting_threshold == 4
    assert config.argument_threshold == 6


def test_config_loads_from_pyproject(tmp_path):
    pyproject = tmp_path / "pyproject.toml"

    pyproject.write_text(
        """
[tool.repodoctor]
complexity_threshold = 5
large_file_threshold = 300
large_function_threshold = 40
nesting_threshold = 3
argument_threshold = 4
""".strip()
    )

    config = ScanConfig.from_pyproject(tmp_path)

    assert config.complexity_threshold == 5
    assert config.large_file_threshold == 300
    assert config.large_function_threshold == 40
    assert config.nesting_threshold == 3
    assert config.argument_threshold == 4


def test_missing_pyproject_uses_defaults(tmp_path):
    config = ScanConfig.from_pyproject(tmp_path)

    assert config == ScanConfig()


def test_invalid_values_use_defaults(tmp_path):
    pyproject = tmp_path / "pyproject.toml"

    pyproject.write_text(
        """
[tool.repodoctor]
complexity_threshold = -5
large_file_threshold = 0
large_function_threshold = "large"
nesting_threshold = false
argument_threshold = 2
""".strip()
    )

    config = ScanConfig.from_pyproject(tmp_path)

    assert config.complexity_threshold == 10
    assert config.large_file_threshold == 500
    assert config.large_function_threshold == 50
    assert config.nesting_threshold == 4
    assert config.argument_threshold == 2


def test_invalid_toml_uses_defaults(tmp_path):
    pyproject = tmp_path / "pyproject.toml"

    pyproject.write_text(
        """
[tool.repodoctor
complexity_threshold = 5
""".strip()
    )

    config = ScanConfig.from_pyproject(tmp_path)

    assert config == ScanConfig()


def test_default_max_file_size():
    config = ScanConfig()

    assert config.max_file_size_bytes == 2_000_000


def test_max_file_size_loads_from_pyproject(tmp_path):
    pyproject = tmp_path / "pyproject.toml"

    pyproject.write_text(
        """
[tool.repodoctor]
max_file_size_bytes = 5000000
""".strip()
    )

    config = ScanConfig.from_pyproject(tmp_path)

    assert config.max_file_size_bytes == 5_000_000


def test_invalid_max_file_size_uses_default(tmp_path):
    pyproject = tmp_path / "pyproject.toml"

    pyproject.write_text(
        """
[tool.repodoctor]
max_file_size_bytes = -1
""".strip()
    )

    config = ScanConfig.from_pyproject(tmp_path)

    assert config.max_file_size_bytes == 2_000_000


def test_scanner_uses_configured_max_file_size(tmp_path):
    pyproject = tmp_path / "pyproject.toml"

    pyproject.write_text(
        """
[tool.repodoctor]
max_file_size_bytes = 10
""".strip()
    )

    from repodoctor.scanner import RepositoryScanner

    scanner = RepositoryScanner(tmp_path)

    assert scanner.file_collector.max_file_size_bytes == 10

def test_unreadable_pyproject_uses_defaults(
    tmp_path,
    monkeypatch,
):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        "[tool.repodoctor]\ncomplexity_threshold = 5\n"
    )

    original_open = Path.open

    def failing_open(self, *args, **kwargs):
        if self == pyproject:
            raise OSError("permission denied")

        return original_open(self, *args, **kwargs)

    monkeypatch.setattr(Path, "open", failing_open)

    config = ScanConfig.from_pyproject(tmp_path)

    assert config == ScanConfig()
