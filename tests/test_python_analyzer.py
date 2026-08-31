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

def test_analyzer_handles_syntax_error(tmp_path: Path):
    source = """
def broken(:
    pass
"""

    file = tmp_path / "broken.py"
    file.write_text(source)

    result = PythonAnalyzer().analyze(file)

    assert result.functions == 0
    assert result.classes == 0
    assert result.todos == 0
    assert result.lines == 3
    assert result.functions_report == []


def test_analyzer_detects_async_functions(tmp_path: Path):
    source = """
async def fetch():
    return True
"""

    file = tmp_path / "async.py"
    file.write_text(source)

    result = PythonAnalyzer().analyze(file)

    assert result.functions == 1
    assert len(result.functions_report) == 1
    assert result.functions_report[0].name == "fetch"


def test_analyzer_detects_fixme(tmp_path: Path):
    source = """
# FIXME: repair this

def hello():
    return True
"""

    file = tmp_path / "fixme.py"
    file.write_text(source)

    result = PythonAnalyzer().analyze(file)

    assert result.todos == 1


def test_analyzer_counts_todo_and_fixme_lines_case_insensitively(
    tmp_path: Path,
):
    source = """
# todo: first
# TODO: second
# FixMe: third
"""

    file = tmp_path / "markers.py"
    file.write_text(source)

    result = PythonAnalyzer().analyze(file)

    assert result.todos == 3


def test_analyzer_generates_function_report(tmp_path: Path):
    source = """
def greet(name, message):
    if name:
        return message
    return "hello"
"""

    file = tmp_path / "functions.py"
    file.write_text(source)

    result = PythonAnalyzer().analyze(file)

    report = result.functions_report[0]

    assert report.name == "greet"
    assert report.file == str(file)
    assert report.line == 2
    assert report.end_line == 5
    assert report.complexity == 2
    assert report.arguments == 2
    assert report.nesting_depth == 1


def test_analyzer_counts_boolean_complexity(tmp_path: Path):
    source = """
def check(a, b, c):
    if a and b and c:
        return True
    return False
"""

    file = tmp_path / "boolean.py"
    file.write_text(source)

    result = PythonAnalyzer().analyze(file)

    report = result.functions_report[0]

    assert report.complexity == 4


def test_analyzer_counts_control_flow_complexity(tmp_path: Path):
    source = """
def process(items):
    for item in items:
        if item:
            while item:
                break
    return items
"""

    file = tmp_path / "flow.py"
    file.write_text(source)

    result = PythonAnalyzer().analyze(file)

    report = result.functions_report[0]

    assert report.complexity == 4
    assert report.nesting_depth == 3


def test_analyzer_counts_try_and_with_nesting(tmp_path: Path):
    source = """
def process(path):
    with open(path) as file:
        try:
            return file.read()
        except OSError:
            return ""
"""

    file = tmp_path / "nesting.py"
    file.write_text(source)

    result = PythonAnalyzer().analyze(file)

    report = result.functions_report[0]

    assert report.complexity == 3
    assert report.nesting_depth == 2


def test_analyzer_does_not_count_nested_function_as_complexity(
    tmp_path: Path,
):
    source = """
def outer():
    if True:
        def inner():
            if False:
                return 1
        return inner()
"""

    file = tmp_path / "nested.py"
    file.write_text(source)

    result = PythonAnalyzer().analyze(file)

    assert result.functions == 2

    outer = next(
        report
        for report in result.functions_report
        if report.name == "outer"
    )

    inner = next(
        report
        for report in result.functions_report
        if report.name == "inner"
    )

    assert outer.complexity == 3
    assert inner.complexity == 2


def test_analyzer_counts_all_argument_types(tmp_path: Path):
    source = """
def configure(posonly, /, normal, *, keyword):
    return True
"""

    file = tmp_path / "arguments.py"
    file.write_text(source)

    result = PythonAnalyzer().analyze(file)

    report = result.functions_report[0]

    assert report.arguments == 3


def test_analyzer_handles_function_without_end_lineno(
    tmp_path: Path,
    monkeypatch,
):
    analyzer = PythonAnalyzer()

    class FakeFunction:
        name = "fake"
        lineno = 7
        args = type(
            "Args",
            (),
            {
                "posonlyargs": [],
                "args": [],
                "kwonlyargs": [],
            },
        )()

    monkeypatch.setattr(
        analyzer,
        "_calculate_complexity",
        lambda function: 1,
    )
    monkeypatch.setattr(
        analyzer,
        "_calculate_nesting",
        lambda function: 0,
    )
    monkeypatch.setattr(
        analyzer,
        "_count_arguments",
        lambda function: 0,
    )

    report = analyzer._analyze_function(
        FakeFunction(),
        tmp_path / "fake.py",
    )

    assert report.name == "fake"
    assert report.line == 7
    assert report.end_line == 7
    assert report.complexity == 1
    assert report.arguments == 0
    assert report.nesting_depth == 0

def test_analyzer_handles_read_os_error(
    tmp_path: Path,
    monkeypatch,
):
    path = tmp_path / "broken.py"
    path.write_text("def hello():\n    return True\n")

    original_read_text = Path.read_text

    def failing_read_text(self, *args, **kwargs):
        if self == path:
            raise OSError("permission denied")

        return original_read_text(
            self,
            *args,
            **kwargs,
        )

    monkeypatch.setattr(
        Path,
        "read_text",
        failing_read_text,
    )

    result = PythonAnalyzer().analyze(path)

    assert result.path == str(path)
    assert result.lines == 0
    assert result.functions == 0
    assert result.classes == 0
    assert result.todos == 0
    assert result.functions_report == []
