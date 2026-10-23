import json

import pytest

from streamstats.errors import InvalidLineError
from streamstats.parsers import parse_csv, parse_jsonl


def test_broken_line_jsonl(tmp_path):
    path = tmp_path / "broken_line.jsonl"

    path.write_text(
        '{"timestamp": "2026-10-23T12:00:00+08:00",'
        '"level": "INFO" ,'
        '"source": "auth",'
        '"message": "correct"}\n'
        "{broken line\n",
        encoding="utf-8",
    )

    skip_lines = {"skip_lines": 0}

    with pytest.raises(InvalidLineError) as error:
        list(parse_jsonl(path, skip_lines, False))

    assert error.value.line_number == 2
    assert skip_lines["skip_lines"] == 0
    assert isinstance(error.value.__cause__, json.JSONDecodeError)


def test_broken_line_jsonl_skip_invalid(tmp_path, caplog):
    path = tmp_path / "broken_line_skip.jsonl"

    path.write_text(
        '{"timestamp": "2026-10-23T12:00:00+08:00",'
        '"level": "INFO" ,'
        '"source": "auth",'
        '"message": "correct"}\n'
        "{broken line\n"
        '{"timestamp": "2026-10-23T12:00:00+08:00",'
        '"level": "INFO" ,'
        '"source": "auth",'
        '"message": "correct"}\n',
        encoding="utf-8",
    )

    skip_lines = {"skip_lines": 0}

    result = list(parse_jsonl(path, skip_lines, True))

    assert skip_lines["skip_lines"] == 1
    assert len(result) == 2
    assert "пропущена строка 2" in caplog.text


def test_broken_line_missing_field_jsonl(tmp_path):
    path = tmp_path / "broken_missing_field.jsonl"

    path.write_text(
        '{"timestamp":"2026-10-20T12:00:00+03:00",'
        '"level":"INFO",'
        '"source":"auth",'
        '"message":"correct"}\n'
        '{"timestamp":"2026-10-20T13:00:00+03:00",'
        '"level":"ERROR",'
        '"source":"auth"}\n'
        '{"timestamp":"2026-10-20T14:00:00+03:00",'
        '"level":"INFO",'
        '"source":"auth",'
        '"message":"correct 2"}\n',
        encoding="utf-8",
    )

    skip_lines = {"skip_lines": 0}

    with pytest.raises(InvalidLineError) as error:
        list(parse_jsonl(path, skip_lines, False))

    assert error.value.line_number == 2
    assert "message" in error.value.reason
    assert skip_lines["skip_lines"] == 0


def test_broken_line_missing_field_jsonl_skip_invalid(tmp_path, caplog):
    path = tmp_path / "broken_missing_field_skip.jsonl"

    path.write_text(
        '{"timestamp":"2026-10-20T12:00:00+03:00",'
        '"level":"INFO",'
        '"source":"auth",'
        '"message":"correct 1"}\n'
        '{"timestamp":"2026-10-20T13:00:00+03:00",'
        '"level":"ERROR",'
        '"source":"auth"}\n'
        '{"timestamp":"2026-10-20T14:00:00+03:00",'
        '"level":"INFO",'
        '"source":"auth",'
        '"message":"correct 2"}\n',
        encoding="utf-8",
    )

    skip_lines = {"skip_lines": 0}

    result = list(parse_jsonl(path, skip_lines, True))

    assert len(result) == 2
    assert skip_lines["skip_lines"] == 1
    assert "пропущена строка 2" in caplog.text
    assert "message" in caplog.text


def test_broken_line_csv(tmp_path):
    path = tmp_path / "broken_line.csv"

    path.write_text(
        "timestamp,level,source,message\n"
        "2026-10-20T12:00:00+03:00,INFO,auth,correct\n"
        "2026-10-20T13:00:00+03:00,ERROR,auth,incorrect,BROKEN\n"
        "2026-10-20T14:00:00+03:00,INFO,auth,correct\n",
        encoding="utf-8",
    )

    skip_lines = {"skip_lines": 0}

    with pytest.raises(InvalidLineError) as error:
        list(parse_csv(path, skip_lines, False))

    assert error.value.line_number == 3
    assert error.value.reason == "лишние значения"
    assert skip_lines["skip_lines"] == 0


def test_broken_line_skip_invalid_csv(tmp_path, caplog):
    path = tmp_path / "broken_line_skip.csv"

    path.write_text(
        "timestamp,level,source,message\n"
        "2026-10-20T12:00:00+03:00,INFO,auth,correct\n"
        "2026-10-20T13:00:00+03:00,ERROR,auth,incorrect,BROKEN\n"
        "2026-10-20T14:00:00+03:00,INFO,auth,correct\n",
        encoding="utf-8",
    )

    skip_lines = {"skip_lines": 0}

    result = list(parse_csv(path, skip_lines, True))

    assert skip_lines["skip_lines"] == 1
    assert len(result) == 2
    assert "пропущена строка 3" in caplog.text


def test_broken_line_missing_value_csv(tmp_path):
    path = tmp_path / "missing_value.csv"

    path.write_text(
        "timestamp,level,source,message\n"
        "2026-10-20T12:00:00+03:00,INFO,auth,correct\n"
        "2026-10-20T13:00:00+03:00,ERROR,auth\n"
        "2026-10-20T14:00:00+03:00,INFO,auth,correct\n",
        encoding="utf-8",
    )

    skip_lines = {"skip_lines": 0}

    with pytest.raises(InvalidLineError) as error:
        list(parse_csv(path, skip_lines, False))

    assert error.value.line_number == 3
    assert "message" in error.value.reason
    assert skip_lines["skip_lines"] == 0


def test_broken_line_missing_value_skip_invalid_csv(tmp_path, caplog):
    path = tmp_path / "missing_value_skip.csv"

    path.write_text(
        "timestamp,level,source,message\n"
        "2026-10-20T12:00:00+03:00,INFO,auth,correct 1\n"
        "2026-10-20T13:00:00+03:00,ERROR,auth\n"
        "2026-10-20T14:00:00+03:00,INFO,auth,correct 2\n",
        encoding="utf-8",
    )

    skip_lines = {"skip_lines": 0}

    result = list(parse_csv(path, skip_lines, True))

    assert len(result) == 2
    assert skip_lines["skip_lines"] == 1
    assert "пропущена строка 3" in caplog.text


def test_broken_header_csv(tmp_path):
    path = tmp_path / "broken_header.csv"

    path.write_text(
        "2026-10-20T12:00:00+03:00,INFO,auth,correct\n"
        "2026-10-20T13:00:00+03:00,ERROR,auth,correct\n",
        encoding="utf-8",
    )

    skip_lines = {"skip_lines": 0}

    with pytest.raises(InvalidLineError) as error:
        list(parse_csv(path, skip_lines, False))

    assert error.value.line_number == 1
    assert error.value.reason == "нет столбца timestamp"
    assert skip_lines["skip_lines"] == 0


def test_broken_header_csv_skip_invalid(tmp_path):
    path = tmp_path / "broken_header_skip.csv"

    path.write_text(
        "2026-10-20T12:00:00+03:00,INFO,auth,correct\n"
        "2026-10-20T13:00:00+03:00,ERROR,auth,correct\n",
        encoding="utf-8",
    )

    skip_lines = {"skip_lines": 0}

    with pytest.raises(InvalidLineError) as error:
        list(parse_csv(path, skip_lines, True))

    assert error.value.line_number == 1
    assert error.value.reason == "нет столбца timestamp"
    assert skip_lines["skip_lines"] == 0


def test_broken_title_message_csv(tmp_path):
    """ошибка в заголовке, поэтому нет смысла делать тест с --skip-invalid, тк это общая ошибка файла, а не одной строки"""
    path = tmp_path / "broken_message.csv"

    path.write_text(
        "timestamp,level,source\n2026-10-20T12:00:00+03:00,INFO,auth\n",
        encoding="utf-8",
    )

    skip_lines = {"skip_lines": 0}

    with pytest.raises(InvalidLineError) as error:
        list(parse_csv(path, skip_lines, False))

    assert error.value.line_number == 1
    assert error.value.reason == "нет столбца message"
    assert skip_lines["skip_lines"] == 0
