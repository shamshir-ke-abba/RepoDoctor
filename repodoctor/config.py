from dataclasses import dataclass


@dataclass(frozen=True)
class ScanConfig:
    """Configuration for repository health analysis."""

    complexity_threshold: int = 10
    large_file_threshold: int = 500
    large_function_threshold: int = 50
    nesting_threshold: int = 4
    argument_threshold: int = 6
