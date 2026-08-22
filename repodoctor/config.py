from dataclasses import dataclass, field
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
    excluded_directories: set[str] = field(
        default_factory=set
    )

    @classmethod
    def from_pyproject(
        cls,
        root: Path,
    ) -> "ScanConfig":
        """Load configuration from pyproject.toml."""

        section = cls._load_section(root)

        if section is None:
            return cls()

        return cls._from_section(section)

    @staticmethod
    def _load_section(
        root: Path,
    ) -> dict | None:
        """Load the RepoDoctor configuration section."""

        pyproject = root / "pyproject.toml"

        if not pyproject.exists():
            return None

        try:
            with pyproject.open("rb") as file:
                data = tomllib.load(file)
        except (OSError, tomllib.TOMLDecodeError):
            return None

        return (
            data
            .get("tool", {})
            .get("repodoctor", {})
        )

    @classmethod
    def _from_section(
        cls,
        section: dict,
    ) -> "ScanConfig":
        """Build configuration from a TOML section."""

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
            excluded_directories=(
                cls._get_excluded_directories(section)
            ),
        )

    @staticmethod
    def _get_excluded_directories(
        section: dict,
    ) -> set[str]:
        """Read configured directories to exclude."""

        value = section.get("exclude", [])

        if not isinstance(value, list):
            return set()

        return {
            item
            for item in value
            if isinstance(item, str) and item
        }

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
