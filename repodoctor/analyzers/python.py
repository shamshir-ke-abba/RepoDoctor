import ast
from pathlib import Path

from repodoctor.models import PythonFileReport


class PythonAnalyzer:
    """Analyze Python source files."""

    def analyze(self, path: Path) -> PythonFileReport:
        source = path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        lines = len(source.splitlines())

        try:
            tree = ast.parse(source)
        except SyntaxError:
            return PythonFileReport(
                path=str(path),
                lines=lines,
                functions=0,
                classes=0,
                todos=0,
            )

        functions = 0
        classes = 0
        todos = 0

        for node in ast.walk(tree):
            if isinstance(
                node,
                (ast.FunctionDef, ast.AsyncFunctionDef),
            ):
                functions += 1

            elif isinstance(node, ast.ClassDef):
                classes += 1

        for line in source.splitlines():
            upper = line.upper()

            if "TODO" in upper or "FIXME" in upper:
                todos += 1

        complexity = self._calculate_complexity(tree)

        return PythonFileReport(
            path=str(path),
            lines=lines,
            functions=functions,
            classes=classes,
            todos=todos,
            complexity=complexity,
        )

    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate a basic cyclomatic complexity score."""

        complexity = 1

        decision_nodes = (
            ast.If,
            ast.For,
            ast.AsyncFor,
            ast.While,
            ast.IfExp,
            ast.ExceptHandler,
            ast.With,
            ast.AsyncWith,
            ast.Assert,
        )

        for node in ast.walk(tree):
            if isinstance(node, decision_nodes):
                complexity += 1

            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1

        return complexity
