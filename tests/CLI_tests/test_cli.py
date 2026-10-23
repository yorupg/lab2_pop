import json
import logging

from typer.testing import CliRunner

from streamstats.__main__ import app

runner = CliRunner()

def test_cli_jsonl(tmp_path):
    path = tmp_path / "logs.jsonl"
    output = tmp_path / "REPORT.json"

    path.write_text(
        '{"timestamp":"2026-10-18T12:00:00+00:00","level":"ERROR","source":"auth","message":" сообщение "}\n',
        encoding = "utf-8",
    )

    result = runner.invoke(
        app,
        ["analyze", str(path), "--format", "jsonl", "--output", str(output)],
    )

    assert result.exit_code == 0
    assert result.stdout.strip() == f"отчёт сохранён: {output}"
    assert output.exists()

    data = json.loads(output.read_text(encoding="utf-8"))

    assert data["count_event"] == 1
    assert data["level_count"]["ERROR"] == 1
    assert data["source_counts"]["auth"] == 1
    assert data["skip_lines"] == 0

    assert data["level_source_counts"] == [
        {"source": "auth", "level": "ERROR", "count": 1}
        ]

    assert data["top_5_source"] == [
        {"source": "auth", "level": "ERROR", "count": 1}
        ]

    assert data["earliest_timestamp"] == "2026-10-18T12:00:00+00:00"
    assert data["latest_timestamp"] == "2026-10-18T12:00:00+00:00"

def test_cli_csv_json_files(tmp_path):
    path_csv = tmp_path / "path_csv.csv"
    path_jsonl = tmp_path / "path_jsonl.jsonl"
    output = tmp_path / "REPORT.json"

    path_csv.write_text(
        "timestamp,level,source,message\n"
        "2026-10-18T12:00:00+00:00,ERROR,auth, correct\n",
        encoding="utf-8",
    )

    path_jsonl.write_text(
        '{"timestamp":"2026-10-18T13:00:00+00:00","level":"CRITICAL","source":"database","message":"Сбой"}\n',
        encoding="utf-8",
    )

    result = runner.invoke(app, ["analyze",
            str(path_csv),
            str(path_jsonl),
            "--format",
            "csv",
            "--format",
            "jsonl",
            "--output",
            str(output),])

    assert result.exit_code == 0
    assert result.stdout.strip() == f"отчёт сохранён: {output}"
    assert output.exists()

    data = json.loads(output.read_text(encoding = "utf-8"))

    assert data["count_event"] == 2
    assert data["level_count"]["ERROR"] == 1
    assert data["level_count"]["CRITICAL"] == 1
    assert data["source_counts"]["auth"] == 1
    assert data["source_counts"]["database"] == 1
    assert data["skip_lines"] == 0

    assert {"source": "auth", "level": "ERROR", "count": 1} in data["top_5_source"]
    assert {"source": "database", "level": "CRITICAL", "count": 1} in data["top_5_source"]

    assert data["earliest_timestamp"] == "2026-10-18T12:00:00+00:00"
    assert data["latest_timestamp"] == "2026-10-18T13:00:00+00:00"

def test_cli_one_format_files(tmp_path):
    path_jsonl_1 = tmp_path / "first_jsonl.jsonl"
    path_jsonl_2 = tmp_path / "second_jsonl.jsonl"
    output = tmp_path / "REPORT.json"

    path_jsonl_1.write_text(
        '{"timestamp":"2026-10-18T12:00:00+00:00","level":"INFO","source":"auth","message":"Вход"}\n',
        encoding="utf-8",
    )

    path_jsonl_2.write_text(
        '{"timestamp":"2026-10-18T13:00:00+00:00","level":"ERROR","source":"database","message":"Ошибка"}\n',
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        [
            "analyze",
            str(path_jsonl_1),
            str(path_jsonl_2),
            "--format",
            "jsonl",
            "--output",
            str(output),
        ],
    )

    assert result.exit_code == 0
    assert output.exists()

    data = json.loads(output.read_text(encoding="utf-8"))

    assert data["count_event"] == 2
    assert data["source_counts"]["auth"] == 1
    assert data["source_counts"]["database"] == 1
    assert data["skip_lines"] == 0

def test_cli_wrong_count_formats(tmp_path):
    path = tmp_path / "file.jsonl"
    output = tmp_path / "REPORT.json"

    path.write_text(
        '{"timestamp":"2026-10-18T12:00:00+00:00","level":"INFO","source":"auth","message":"Вход"}\n',
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        [
            "analyze",
            str(path),
            "--format",
            "jsonl",
            "--format",
            "csv",
            "--output",
            str(output),
        ],
    )

    assert result.exit_code == 2
    assert not output.exists()
    assert "введите один --format" in result.stderr

def test_cli_unsupported_format(tmp_path, caplog):
    path = tmp_path / "file_incorrect_format.txt"
    output = tmp_path / "REPORT.json"

    path.write_text("текстовый файл не поддерживается\n", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "analyze",
            str(path),
            "--format",
            "txt",
            "--output",
            str(output),
        ],
    )

    assert result.exit_code == 2
    assert not output.exists()
    assert any(
        record.levelno == logging.ERROR
        and "неподдерживаемый формат файла" in record.getMessage()
        and "txt" in record.getMessage()
        for record in caplog.records
    )

def test_cli_missing_file(tmp_path, caplog):
    path = tmp_path / "missing_file.jsonl"
    output = tmp_path / "REPORT.json"

    result = runner.invoke(
        app,
        [
            "analyze",
            str(path),
            "--format",
            "jsonl",
            "--output",
            str(output),
        ],
    )

    assert result.exit_code == 2
    assert not output.exists()
    assert any(
        record.levelno == logging.ERROR
        and "не найден файл" in record.getMessage()
        and str(path) in record.getMessage()
        for record in caplog.records
    )

def test_cli_one_input_output(tmp_path, caplog):
    path = tmp_path / "input_and_output.jsonl"

    path.write_text(
        '{"timestamp":"2026-10-18T12:00:00+00:00","level":"INFO","source":"auth","message":"Вход"}\n',
        encoding="utf-8",
    )

    text = path.read_text(encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "analyze",
            str(path),
            "--format",
            "jsonl",
            "--output",
            str(path),
        ],
    )

    assert result.exit_code == 2
    assert path.read_text(encoding="utf-8") == text
    assert any(
        record.levelno == logging.ERROR
        and "входной файл совпадает с выходным" in record.getMessage()
        for record in caplog.records
    )


def test_cli_skip_two_lines(tmp_path, caplog):
    path_error_1 = tmp_path / "error_line_1.jsonl"
    path_error_2 = tmp_path / "error_line_2.jsonl"
    output = tmp_path / "REPORT.json"

    path_error_1.write_text(
        "not json\n"
        '{"timestamp":"2026-10-18T12:00:00+00:00","level":"INFO","source":"auth","message":"Вход"}\n',
        encoding="utf-8",
    )

    path_error_2.write_text(
        '{"timestamp":"2026-10-18T13:00:00+00:00","level":"ERROR","source":"database","message":"Ошибка"}\n'
        '{"timestamp":"2026-10-18T13:00:00+00:00","level":"ERROR","source":"database","message":"Ошибка"}\n'
        "broken json\n",
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        [
            "analyze",
            str(path_error_1),
            str(path_error_2),
            "--format",
            "jsonl",
            "--skip-invalid",
            "--output",
            str(output),
        ],
    )

    assert result.exit_code == 0
    assert output.exists()

    data = json.loads(output.read_text(encoding="utf-8"))

    assert data["count_event"] == 3
    assert data["skip_lines"] == 2
    assert data["source_counts"]["auth"] == 1
    assert data["source_counts"]["database"] == 2

    warnings = [
        record
        for record in caplog.records
        if record.levelno == logging.WARNING
    ]

    assert len(warnings) == 2

def test_cli_two_lines_error(tmp_path, caplog):
    path_correct = tmp_path / "line_correct.jsonl"
    path_error_2 = tmp_path / "error_line_2.jsonl"
    output = tmp_path / "REPORT.json"

    path_correct.write_text(
        '{"timestamp":"2026-10-18T12:00:00+00:00","level":"INFO","source":"auth","message":"Вход"}\n',
        encoding="utf-8",
    )

    path_error_2.write_text(
        '{"timestamp":"2026-10-18T13:00:00+00:00","level":"ERROR","source":"database","message":"Ошибка"}\n'
        '{"timestamp":"2026-10-18T13:00:00+00:00","level":"ERROR","source":"database","message":"Ошибка"}\n'
        "broken json\n",
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        [
            "analyze",
            str(path_correct),
            str(path_error_2),
            "--format",
            "jsonl",
            "--output",
            str(output),
        ],
    )

    assert result.exit_code == 2
    assert not output.exists()
    assert any(
        record.levelno == logging.ERROR
        and str(path_error_2) in record.getMessage()
        and "строка 3" in record.getMessage()
        for record in caplog.records
    )
