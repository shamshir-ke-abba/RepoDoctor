from pathlib import Path


class FileCollector:
    """Discover repository files using shared scanning rules."""

    IGNORED_DIRECTORIES = {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        "node_modules",
        ".mypy_cache",
        ".pytest_cache",
    }

    def __init__(
        self,
        root: Path,
        max_file_size_bytes: int = 2_000_000,
        excluded_directories: set[str] | None = None,
    ):
        self.root = root.resolve()
        self.max_file_size_bytes = max_file_size_bytes
        self.excluded_directories = (
            set(excluded_directories or ())
        )

    def files(self):
        """Yield eligible repository files in deterministic order."""

        paths = []

        ignored_directories = (
            self.IGNORED_DIRECTORIES
            | self.excluded_directories
        )

        for path in self.root.rglob("*"):
            if not path.is_file():
                continue

            if any(
                part in ignored_directories
                for part in path.parts
            ):
                continue

            try:
                if (
                    path.stat().st_size
                    > self.max_file_size_bytes
                ):
                    continue
            except OSError:
                continue

            paths.append(path)

        yield from sorted(paths)

    def python_files(self):
        """Yield eligible Python files."""

        for path in self.files():
            if path.suffix == ".py":
                yield path
