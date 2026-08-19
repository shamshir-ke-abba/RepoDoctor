from pathlib import Path


class StructureAnalyzer:
    """Analyze repository structure."""

    def analyze(self, root: Path) -> dict:
        return {
            "has_readme": self._has_readme(root),
            "has_gitignore": (root / ".gitignore").exists(),
            "is_git_repo": (root / ".git").is_dir(),
        }

    def _has_readme(self, root: Path) -> bool:
        possible_names = (
            "README",
            "README.md",
            "README.txt",
            "README.rst",
        )

        return any(
            (root / name).exists()
            for name in possible_names
        )
