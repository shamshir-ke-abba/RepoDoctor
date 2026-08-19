from pathlib import Path

from repodoctor.analyzers.python import PythonAnalyzer


def test_analyzer_counts_functions_and_classes(tmp_path: Path):
    source = """
class Example:
    def hello(self):
        return "hello"


def add(a, b):
    return a + b
"""

    file = tmp_path / "example.py"
    file.write_text(source)

    result = PythonAnalyzer().analyze(file)

    assert result.functions == 2
    assert result.classes == 1
    assert result.lines > 0


def test_analyzer_detects_todo(tmp_path: Path):
    source = """
# TODO: fix this later

def hello():
    return True
"""

    file = tmp_path / "todo.py"
    file.write_text(source)

    result = PythonAnalyzer().analyze(file)

    assert result.todos == 1
