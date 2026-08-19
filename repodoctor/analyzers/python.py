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

                report = self._analyze_function(
                    node,
                    path,
                )

                function_reports.append(report)

            elif isinstance(
                node,
                ast.ClassDef,
            ):

                classes += 1

        for line in source.splitlines():

            upper = line.upper()

            if "TODO" in upper or "FIXME" in upper:
                todos += 1

        return PythonFileReport(
            path=str(path),
            lines=lines,
            functions=functions,
            classes=classes,
            todos=todos,
            functions_report=function_reports,
        )

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

            elif isinstance(
                node,
                ast.BoolOp,
            ):
                complexity += (
                    len(node.values) - 1
                )

        return complexity

    def _calculate_nesting(
        self,
        function: ast.AST,
    ) -> int:

        max_depth = 0

        nesting_nodes = (
            ast.If,
            ast.For,
            ast.AsyncFor,
            ast.While,
            ast.With,
            ast.AsyncWith,
            ast.Try,
        )

        def walk(
            node: ast.AST,
            depth: int,
        ):

            nonlocal max_depth

            if isinstance(
                node,
                nesting_nodes,
            ):
                depth += 1

                max_depth = max(
                    max_depth,
                    depth,
                )

            for child in ast.iter_child_nodes(
                node
            ):

                if isinstance(
                    child,
                    (
                        ast.FunctionDef,
                        ast.AsyncFunctionDef,
                    ),
                ):
                    continue

                walk(child, depth)

        for child in ast.iter_child_nodes(
            function
        ):
            walk(child, 0)

        return max_depth

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
