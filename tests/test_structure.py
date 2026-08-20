from pathlib import Path

from repodoctor.analyzers.structure import StructureAnalyzer


def test_empty_repository_has_no_structure_files(
    tmp_path: Path,
):
    result = StructureAnalyzer().analyze(tmp_path)

    assert result == {
        "has_readme": False,
        "has_gitignore": False,
        "is_git_repo": False,
    }


def test_detects_readme(tmp_path: Path):
    (tmp_path / "README").write_text("Project")

    result = StructureAnalyzer().analyze(tmp_path)

    assert result["has_readme"] is True


def test_detects_readme_md(tmp_path: Path):
    (tmp_path / "README.md").write_text("# Project")

    result = StructureAnalyzer().analyze(tmp_path)

    assert result["has_readme"] is True


def test_detects_readme_txt(tmp_path: Path):
    (tmp_path / "README.txt").write_text("Project")

    result = StructureAnalyzer().analyze(tmp_path)

    assert result["has_readme"] is True


def test_detects_readme_rst(tmp_path: Path):
    (tmp_path / "README.rst").write_text("Project")

    result = StructureAnalyzer().analyze(tmp_path)

    assert result["has_readme"] is True


def test_detects_all_supported_readme_names(
    tmp_path: Path,
):
    names = (
        "README",
        "README.md",
        "README.txt",
        "README.rst",
    )

    for name in names:
        (tmp_path / name).write_text("Project")

    result = StructureAnalyzer().analyze(tmp_path)

    assert result["has_readme"] is True


def test_detects_gitignore(tmp_path: Path):
    (tmp_path / ".gitignore").write_text(
        "__pycache__/\n"
    )

    result = StructureAnalyzer().analyze(tmp_path)

    assert result["has_gitignore"] is True


def test_detects_git_directory(tmp_path: Path):
    (tmp_path / ".git").mkdir()

    result = StructureAnalyzer().analyze(tmp_path)

    assert result["is_git_repo"] is True


def test_complete_repository_structure(
    tmp_path: Path,
):
    (tmp_path / "README.md").write_text("# Project")
    (tmp_path / ".gitignore").write_text(
        "__pycache__/\n"
    )
    (tmp_path / ".git").mkdir()

    result = StructureAnalyzer().analyze(tmp_path)

    assert result == {
        "has_readme": True,
        "has_gitignore": True,
        "is_git_repo": True,
    }


def test_readme_detection_is_case_sensitive(
    tmp_path: Path,
):
    (tmp_path / "readme.md").write_text("# Project")

    result = StructureAnalyzer().analyze(tmp_path)

    assert result["has_readme"] is False


def test_git_directory_must_be_directory(
    tmp_path: Path,
):
    (tmp_path / ".git").write_text("not a directory")

    result = StructureAnalyzer().analyze(tmp_path)

    assert result["is_git_repo"] is False


def test_gitignore_must_exist_at_repository_root(
    tmp_path: Path,
):
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / ".gitignore").write_text("*.pyc")

    result = StructureAnalyzer().analyze(tmp_path)

    assert result["has_gitignore"] is False


def test_readme_must_exist_at_repository_root(
    tmp_path: Path,
):
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "README.md").write_text("# Nested")

    result = StructureAnalyzer().analyze(tmp_path)

    assert result["has_readme"] is False
