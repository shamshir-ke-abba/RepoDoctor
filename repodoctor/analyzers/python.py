import ast
from pathlib import Path

from repodoctor.models import (
    FunctionReport,
    PythonFileReport,
)


class PythonAnalyzer:
    """Analyze Python source files."""

    def analyze(self, path: Path) -> PythonFileReport:
        source = path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        lines = len(source.splitlines())
        tree = self._parse_source(source)

        if tree is None:
            return self._empty_report(path, lines)

        functions, classes, function_reports = (
            self._analyze_tree(tree, path)
        )

        todos = self._count_todos(source)

        return PythonFileReport(
            path=str(path),
            lines=lines,
            functions=functions,
            classes=classes,
            todos=todos,
            functions_report=function_reports,
        )

    def _parse_source(
        self,
        source: str,
    ) -> ast.AST | None:
        """Parse Python source and return its AST."""

        try:
            return ast.parse(source)
        except SyntaxError:
            return None

    def _empty_report(
        self,
        path: Path,
        lines: int,
    ) -> PythonFileReport:
        """Build a report for invalid Python source."""

        return PythonFileReport(
            path=str(path),
            lines=lines,
            functions=0,
            classes=0,
            todos=0,
        )

    def _analyze_tree(
        self,
        tree: ast.AST,
        path: Path,
    ) -> tuple[int, int, list[FunctionReport]]:
        """Collect functions, classes, and function reports."""

        functions = 0
        classes = 0
        function_reports = []

        for node in ast.walk(tree):
            if isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                ),
            ):
                functions += 1
                function_reports.append(
                    self._analyze_function(
                        node,
                        path,
                    )
                )

            elif isinstance(node, ast.ClassDef):
                classes += 1

        return functions, classes, function_reports

    def _count_todos(self, source: str) -> int:
        """Count TODO and FIXME comments."""

        todos = 0

        for line in source.splitlines():
            upper = line.upper()

            if "TODO" in upper or "FIXME" in upper:
                todos += 1

        return todos

    def _analyze_function(
        self,
        function: ast.AST,
        path: Path,
    ) -> FunctionReport:
        complexity = self._calculate_complexity(
            function
        )

        nesting = self._calculate_nesting(
            function
        )

        arguments = self._count_arguments(
            function
        )

        end_line = getattr(
            function,
            "end_lineno",
            function.lineno,
        )

        return FunctionReport(
            name=function.name,
            file=str(path),
            line=function.lineno,
            end_line=end_line,
            complexity=complexity,
            arguments=arguments,
            nesting_depth=nesting,
        )

    def _calculate_complexity(
        self,
        function: ast.AST,
    ) -> int:
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

        for node in ast.walk(function):
            if node is function:
                continue

            # Don't count nested functions.
            if isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                ),
            ):
                continue

            if isinstance(
                node,
                decision_nodes,
            ):
                complexity += 1

            elif isinstance(node, ast.BoolOp):
                complexity += (
                    len(node.values) - 1
                )

        return complexity

    def _calculate_nesting(
        self,
        function: ast.AST,
    ) -> int:
        """Calculate the maximum nesting depth."""

        nesting_nodes = (
            ast.If,
            ast.For,
            ast.AsyncFor,
            ast.While,
            ast.With,
            ast.AsyncWith,
            ast.Try,
        )

        max_depth = 0

        for child in ast.iter_child_nodes(function):
            max_depth = max(
                max_depth,
                self._nesting_depth(
                    child,
                    0,
                    nesting_nodes,
                ),
            )

        return max_depth

    def _nesting_depth(
        self,
        node: ast.AST,
        depth: int,
        nesting_nodes: tuple,
    ) -> int:
        """Find the deepest nesting level below a node."""

        if isinstance(node, nesting_nodes):
            depth += 1

        max_depth = depth

        for child in ast.iter_child_nodes(node):
            if self._is_nested_function(child):
                continue

            max_depth = max(
                max_depth,
                self._nesting_depth(
                    child,
                    depth,
                    nesting_nodes,
                ),
            )

        return max_depth

    def _is_nested_function(
        self,
        node: ast.AST,
    ) -> bool:
        """Return whether an AST node defines a nested function."""

        return isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        )

    def _count_arguments(
        self,
        function: ast.AST,
    ) -> int:
        arguments = function.args

        return (
            len(arguments.posonlyargs)
            + len(arguments.args)
            + len(arguments.kwonlyargs)
        )
