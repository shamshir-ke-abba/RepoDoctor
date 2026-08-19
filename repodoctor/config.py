from dataclasses import dataclass
from pathlib import Path
import tomllib


@dataclass(frozen=True)
class ScanConfig:
    """Configuration for repository health analysis."""

    complexity_threshold: int = 10
    large_file_threshold: int = 500
    large_function_threshold: int = 50
    nesting_threshold: int = 4
    argument_threshold: int = 6

    @classmethod
    def from_pyproject(
        cls,
        root: Path,
    ) -> "ScanConfig":
        """Load scanner configuration from pyproject.toml."""

        pyproject = root / "pyproject.toml"

        if not pyproject.is_file():
            return cls()

        try:
            with pyproject.open("rb") as file:
                data = tomllib.load(file)
        except (OSError, tomllib.TOMLDecodeError):
            return cls()

        values = data.get("tool", {}).get(
            "repodoctor",
            {},
        )

        defaults = cls()

        return cls(
            complexity_threshold=_positive_int(
                values.get(
                    "complexity_threshold",
                    defaults.complexity_threshold,
                ),
                defaults.complexity_threshold,
            ),
            large_file_threshold=_positive_int(
                values.get(
                    "large_file_threshold",
                    defaults.large_file_threshold,
                ),
                defaults.large_file_threshold,
            ),
            large_function_threshold=_positive_int(
                values.get(
                    "large_function_threshold",
                    defaults.large_function_threshold,
                ),
                defaults.large_function_threshold,
            ),
            nesting_threshold=_positive_int(
                values.get(
                    "nesting_threshold",
                    defaults.nesting_threshold,
                ),
                defaults.nesting_threshold,
            ),
            argument_threshold=_positive_int(
                values.get(
                    "argument_threshold",
                    defaults.argument_threshold,
                ),
                defaults.argument_threshold,
            ),
        )


def _positive_int(
    value,
    default: int,
) -> int:
    """Return a valid positive integer or the default."""

    if isinstance(value, bool):
        return default

    if isinstance(value, int) and value > 0:
        return value

    return default
