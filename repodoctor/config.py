from dataclasses import dataclass
from pathlib import Path
import tomllib


@dataclass
class ScanConfig:
    """Configuration for repository scanning."""

    complexity_threshold: int = 10
    large_file_threshold: int = 500
    large_function_threshold: int = 50
    nesting_threshold: int = 4
    argument_threshold: int = 6
    max_file_size_bytes: int = 2_000_000

    @classmethod
    def from_pyproject(
        cls,
        root: Path,
    ) -> "ScanConfig":
        """Load configuration from pyproject.toml."""

        pyproject = root / "pyproject.toml"

        if not pyproject.exists():
            return cls()

        try:
            with pyproject.open("rb") as file:
                data = tomllib.load(file)
        except (OSError, tomllib.TOMLDecodeError):
            return cls()

        section = (
            data
            .get("tool", {})
            .get("repodoctor", {})
        )

        return cls(
            complexity_threshold=cls._get_int(
                section,
                "complexity_threshold",
                cls.complexity_threshold,
            ),
            large_file_threshold=cls._get_int(
                section,
                "large_file_threshold",
                cls.large_file_threshold,
            ),
            large_function_threshold=cls._get_int(
                section,
                "large_function_threshold",
                cls.large_function_threshold,
            ),
            nesting_threshold=cls._get_int(
                section,
                "nesting_threshold",
                cls.nesting_threshold,
            ),
            argument_threshold=cls._get_int(
                section,
                "argument_threshold",
                cls.argument_threshold,
            ),
            max_file_size_bytes=cls._get_int(
                section,
                "max_file_size_bytes",
                cls.max_file_size_bytes,
            ),
        )

    @staticmethod
    def _get_int(
        section: dict,
        key: str,
        default: int,
    ) -> int:
        """Read a positive integer configuration value."""

        value = section.get(key, default)

        if isinstance(value, bool):
            return default

        if isinstance(value, int) and value > 0:
            return value

        return default
