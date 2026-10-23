import pytest

from streamstats.errors import InvalidLineError
from streamstats.parsers import parse_csv, parse_jsonl

"""тесты jsonl"""


def test_empty_file_jsonl(tmp_path):
    path = tmp_path / "test_empty_file.jsonl"

    path.write_text("", encoding="utf-8")

    skip_lines = {"skip_lines": 0}

    with pytest.raises(InvalidLineError) as error:
        list(parse_jsonl(path, skip_lines, False))

    assert error.value.reason == "пустой файл"
    assert error.value.line_number == 1
    assert skip_lines["skip_lines"] == 0


def test_empty_oneline_file_jsonl(tmp_path):
    path = tmp_path / "test_empty_file.jsonl"

    path.write_text("\n", encoding="utf-8")

    skip_lines = {"skip_lines": 0}

    with pytest.raises(InvalidLineError) as error:
        list(parse_jsonl(path, skip_lines, False))

    assert error.value.reason == "пустая строка"
    assert error.value.line_number == 1
    assert skip_lines["skip_lines"] == 0


def test_empty_file_jsonl_skip_invalid(tmp_path, caplog):
    path = tmp_path / "test_empty_file_skip.jsonl"

    path.write_text("", encoding="utf-8")

    skip_lines = {"skip_lines": 0}

    result = list(parse_jsonl(path, skip_lines, True))

    assert skip_lines["skip_lines"] == 0
    assert len(result) == 0
    assert "пустой файл" in caplog.text


def test_empty_line_json(tmp_path):
    path = tmp_path / "test_empty_line.jsonl"

    path.write_text(
        '{"timestamp":"2026-10-20T12:00:00+03:00",'
        '"level":"INFO",'
        '"source":"auth",'
        '"message":"correct file"}\n'
        "\n"
        '{"timestamp":"2026-10-20T12:00:00+03:00",'
        '"level":"TEST",'
        '"source":"auth",'
        '"message":"incorrect file"}\n',
        encoding="utf-8",
    )

    skip_lines = {"skip_lines": 0}

    with pytest.raises(InvalidLineError) as error:
        list(parse_jsonl(path, skip_lines, False))

    assert error.value.reason == "пустая строка"
    assert error.value.line_number == 2
    assert skip_lines["skip_lines"] == 0


def test_empty_line_json_skip_invalid(tmp_path, caplog):
    path = tmp_path / "test_empty_line_skip.jsonl"

    path.write_text(
        '{"timestamp":"2026-10-20T12:00:00+03:00",'
        '"level":"INFO",'
        '"source":"auth",'
        '"message":"correct file"}\n'
        "\n"
        '{"timestamp":"2026-10-20T12:00:00+03:00",'
        '"level":"ERROR",'
        '"source":"auth",'
        '"message":"incorrect file"}\n',
        encoding="utf-8",
    )

    skip_lines = {"skip_lines": 0}

    result = list(parse_jsonl(path, skip_lines, True))

    assert skip_lines["skip_lines"] == 1
    assert len(result) == 2
    assert "пропущена строка 2" in caplog.text


"""тесты csv"""


def test_empty_file_csv(tmp_path):
    path = tmp_path / "test_empty_file.csv"

    path.write_text("", encoding="utf-8")

    skip_lines = {"skip_lines": 0}

    with pytest.raises(InvalidLineError) as error:
        list(parse_csv(path, skip_lines, False))

    assert error.value.line_number == 1
    assert skip_lines["skip_lines"] == 0
    assert error.value.reason == "пустой файл"


def test_empty_file_csv_skip_invalid(tmp_path, caplog):
    path = tmp_path / "test_empty_file_skip.csv"

    path.write_text("", encoding="utf-8")

    skip_lines = {"skip_lines": 0}

    result = list(parse_csv(path, skip_lines, True))

    assert len(result) == 0
    assert skip_lines["skip_lines"] == 0
    assert "пустой файл" in caplog.text


def test_empty_line_csv(tmp_path):
    path = tmp_path / "test_empty_line.csv"

    path.write_text(
        "timestamp,level,source,message\n"
        "2026-10-20T12:00:00+03:00,INFO,auth,correct 1\n"
        "\n"
        "2026-10-20T13:00:00+03:00,ERROR,auth,correct 2\n",
        encoding="utf-8",
    )

    skip_lines = {"skip_lines": 0}

    result = list(parse_csv(path, skip_lines, False))
    """пустая строка игнорируется с --skip-invalid и без него"""
    assert len(result) == 2
    assert skip_lines["skip_lines"] == 0
    assert result[0].message == "correct 1"
    assert result[1].message == "correct 2"


def test_only_header_csv(tmp_path):
    path = tmp_path / "test_only_header.csv"

    path.write_text("timestamp,level,source,message\n", encoding="utf-8")

    skip_lines = {"skip_lines": 0}

    result = list(parse_csv(path, skip_lines, False))
    """тк пустая строка игнорируется независимо от наличия --skip-invalid результат будет одинаковым с этой опцией и без нее"""

    assert len(result) == 0
    assert skip_lines["skip_lines"] == 0
