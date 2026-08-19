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


def test_fail_under_fails(
    monkeypatch,
    tmp_path,
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
            "101",
        ],
    )

    try:
        main()
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError(
            "Expected argparse failure"
        )


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
