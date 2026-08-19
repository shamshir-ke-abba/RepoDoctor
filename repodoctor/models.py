from dataclasses import dataclass, field


@dataclass
class FunctionReport:
    name: str
    file: str
    line: int
    end_line: int
    complexity: int
    arguments: int
    nesting_depth: int

    @property
    def lines(self) -> int:
        return self.end_line - self.line + 1


@dataclass
class PythonFileReport:
    path: str
    lines: int
    functions: int
    classes: int
    todos: int
    functions_report: list[FunctionReport] = field(
        default_factory=list
    )


@dataclass
class GitReport:
    is_repo: bool = False
    branch: str = ""
    commits: int = 0
    clean: bool = True
    untracked: int = 0
    modified: int = 0
    remote: bool = False

@dataclass
class RepositoryReport:
    path: str

    python_files: int = 0
    total_lines: int = 0
    total_functions: int = 0
    total_classes: int = 0
    total_todos: int = 0

    large_files: list[str] = field(
        default_factory=list
    )

    complex_functions: list[FunctionReport] = field(
        default_factory=list
    )

    large_functions: list[FunctionReport] = field(
        default_factory=list
    )

    deep_functions: list[FunctionReport] = field(
        default_factory=list
    )

    argument_heavy_functions: list[FunctionReport] = field(
        default_factory=list
    )

    security_findings: list = field(
        default_factory=list
    )

    git: GitReport = field(
        default_factory=GitReport
    )

    has_readme: bool = False
    has_gitignore: bool = False
    is_git_repo: bool = False

    recommendations: list[str] = field(
        default_factory=list
    )

    warnings: list[str] = field(
        default_factory=list
    )

    successes: list[str] = field(
        default_factory=list
    )

    health_score: int = 100
