from dataclasses import dataclass, field


@dataclass
class PythonFileReport:
    path: str
    lines: int
    functions: int
    classes: int
    todos: int
    complexity: int = 0


@dataclass
class RepositoryReport:
    path: str

    python_files: int = 0
    total_lines: int = 0
    total_functions: int = 0
    total_classes: int = 0
    total_todos: int = 0

    large_files: list[str] = field(default_factory=list)
    complex_functions: list[str] = field(default_factory=list)

    has_readme: bool = False
    has_gitignore: bool = False
    is_git_repo: bool = False

    warnings: list[str] = field(default_factory=list)
    successes: list[str] = field(default_factory=list)

    health_score: int = 100
