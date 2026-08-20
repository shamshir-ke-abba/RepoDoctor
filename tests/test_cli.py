import json

from repodoctor.cli import main


def test_cli_runs(monkeypatch, tmp_path, capsys):
    (tmp_path / "hello.py").write_text(
        'print("hello")\n'
    )

    monkeypatch.setattr(
        "sys.argv",
        ["repodoctor", str(tmp_path)],
    )

    main()

    output = capsys.readouterr().out

    assert "REPO DOCTOR" in output
    assert "HEALTH SCORE" in output


def test_cli_json_output(
    monkeypatch,
    tmp_path,
    capsys,
):
    (tmp_path / "hello.py").write_text(
        'print("hello")\n'
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "repodoctor",
            str(tmp_path),
            "--format",
            "json",
        ],
    )

    main()

    output = capsys.readouterr().out
    data = json.loads(output)

    assert "health_score" in data
    assert "python_files" in data


def test_fail_under_fails_for_invalid_high_value(
    monkeypatch,
    tmp_path,
    capsys,
):
    monkeypatch.setattr(
        "sys.argv",
        [
            "repodoctor",
            str(tmp_path),
            "--fail-under",
            "101",
        ],
    )

    try:
        main()
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError(
            "Expected argparse validation failure"
        )

    output = capsys.readouterr().out

    assert "--fail-under must be between 0 and 100" in output


def test_fail_under_fails_for_invalid_low_value(
    monkeypatch,
    tmp_path,
    capsys,
):
    monkeypatch.setattr(
        "sys.argv",
        [
            "repodoctor",
            str(tmp_path),
            "--fail-under",
            "-1",
        ],
    )

    try:
        main()
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError(
            "Expected argparse validation failure"
        )

    output = capsys.readouterr().out

    assert "--fail-under must be between 0 and 100" in output


def test_fail_under_passes(
    monkeypatch,
    tmp_path,
    capsys,
):
    (tmp_path / "hello.py").write_text(
        'print("hello")\n'
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "repodoctor",
            str(tmp_path),
            "--fail-under",
            "0",
        ],
    )

    main()

    output = capsys.readouterr().out

    assert "PASS:" in output


def test_fail_under_fails_for_low_score(
    monkeypatch,
    tmp_path,
    capsys,
):
    (tmp_path / "hello.py").write_text(
        'API_KEY = "fake_secret_key_123456"\n'
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "repodoctor",
            str(tmp_path),
            "--fail-under",
            "100",
        ],
    )

    try:
        main()
    except SystemExit as exc:
        assert exc.code == 1
    else:
        raise AssertionError(
            "Expected health threshold failure"
        )

    output = capsys.readouterr().out

    assert "FAIL:" in output


def test_cli_rejects_missing_path(
    monkeypatch,
    tmp_path,
    capsys,
):
    missing = tmp_path / "does-not-exist"

    monkeypatch.setattr(
        "sys.argv",
        ["repodoctor", str(missing)],
    )

    try:
        main()
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError(
            "Expected missing path failure"
        )

    output = capsys.readouterr().out

    assert "Path does not exist" in output


def test_cli_rejects_file_path(
    monkeypatch,
    tmp_path,
    capsys,
):
    file = tmp_path / "hello.py"
    file.write_text("print('hello')\n")

    monkeypatch.setattr(
        "sys.argv",
        ["repodoctor", str(file)],
    )

    try:
        main()
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError(
            "Expected directory validation failure"
        )

    output = capsys.readouterr().out

    assert "Path is not a directory" in output
