import pytest

from streamstats.__main__ import read_events
from streamstats.errors import InvalidLineError


def test_some_files_csv_jsonl(tmp_path):
    path1 = tmp_path / "file1.jsonl"
    path2 = tmp_path / "file2.csv"

    path1.write_text(
        '{"timestamp":"2026-10-23T12:00:00+03:00",'
        '"level":"INFO",'
        '"source":"auth",'
        '"message":"correct jsonl 1"}\n',
        encoding="utf-8",
    )

    path2.write_text(
        "timestamp,level,source,message\n"
        "2026-10-23T13:00:00+03:00,ERROR,auth,correct csv 2\n",
        encoding="utf-8",
    )

    skip_lines = {"skip_lines": 0}

    result = list(
        read_events([str(path1), str(path2)], skip_lines, ["jsonl", "csv"], False)
    )

    assert len(result) == 2
    assert skip_lines["skip_lines"] == 0

    assert result[0].message == "correct jsonl 1"
    assert result[1].message == "correct csv 2"

    assert result[0].level == "INFO"
    assert result[1].level == "ERROR"


def test_some_files_jsonl(tmp_path):
    path1 = tmp_path / "file_jsonl1.jsonl"
    path2 = tmp_path / "file_jsonl2.jsonl"

    path1.write_text(
        '{"timestamp":"2026-10-23T12:00:00+03:00",'
        '"level":"INFO",'
        '"source":"auth",'
        '"message":"first"}\n',
        encoding="utf-8",
    )

    path2.write_text(
        '{"timestamp":"2026-10-23T13:00:00+03:00",'
        '"level":"ERROR",'
        '"source":"auth",'
        '"message":"second"}\n',
        encoding="utf-8",
    )

    skip_lines = {"skip_lines": 0}

    result = list(
        read_events([str(path1), str(path2)], skip_lines, ["jsonl", "jsonl"], False)
    )

    assert len(result) == 2
    assert skip_lines["skip_lines"] == 0

    assert result[0].message == "first"
    assert result[1].message == "second"


def test_some_files_csv(tmp_path):
    path1 = tmp_path / "file_csv1.csv"
    path2 = tmp_path / "file_csv2.csv"

    path1.write_text(
        "timestamp,level,source,message\n"
        "2026-10-23T12:00:00+03:00,INFO,auth1,first_correct\n",
        encoding="utf-8",
    )

    path2.write_text(
        "timestamp,level,source,message\n"
        "2026-10-23T13:00:00+03:00,ERROR,auth2,second_correct\n",
        encoding="utf-8",
    )

    skip_lines = {"skip_lines": 0}

    result = list(
        read_events([str(path1), str(path2)], skip_lines, ["csv", "csv"], False)
    )

    assert len(result) == 2
    assert skip_lines["skip_lines"] == 0

    assert result[0].message == "first_correct"
    assert result[1].message == "second_correct"

    assert result[0].level == "INFO"
    assert result[1].level == "ERROR"

    assert result[0].source == "auth1"
    assert result[1].source == "auth2"


def test_some_files_incorrect_second(tmp_path):
    path1 = tmp_path / "first_correct.jsonl"
    path2 = tmp_path / "second_incorrect.jsonl"

    path1.write_text(
        '{"timestamp":"2026-10-23T12:00:00+03:00",'
        '"level":"INFO",'
        '"source":"auth",'
        '"message":"correct"}\n',
        encoding="utf-8",
    )

    path2.write_text('{"incorrect"}\n', encoding="utf-8")

    skip_lines = {"skip_lines": 0}

    with pytest.raises(InvalidLineError) as error:
        list(
            read_events([str(path1), str(path2)], skip_lines, ["jsonl", "jsonl"], False)
        )

    assert error.value.line_number == 1
    assert str(path2) == str(error.value.file_path)
    assert skip_lines["skip_lines"] == 0


def test_some_files_incorrect_second_skip_invalid(tmp_path, caplog):
    path1 = tmp_path / "first_correct.jsonl"
    path2 = tmp_path / "second_incorrect.jsonl"

    path1.write_text(
        '{"timestamp":"2026-10-23T12:00:00+03:00",'
        '"level":"INFO",'
        '"source":"auth",'
        '"message":"first"}\n',
        encoding="utf-8",
    )

    path2.write_text(
        '{"incorrect"}\n'
        '{"timestamp":"2026-10-23T13:00:00+03:00",'
        '"level":"ERROR",'
        '"source":"auth",'
        '"message":"second"}\n',
        encoding="utf-8",
    )

    skip_lines = {"skip_lines": 0}

    result = list(
        read_events([str(path1), str(path2)], skip_lines, ["jsonl", "jsonl"], True)
    )

    assert len(result) == 2
    assert skip_lines["skip_lines"] == 1

    assert result[0].message == "first"
    assert result[1].message == "second"

    assert "пропущена строка 1" in caplog.text
    assert str(path2) in caplog.text


def test_some_files_empty_first_skip_invalid(tmp_path, caplog):
    path1 = tmp_path / "first_empty.jsonl"
    path2 = tmp_path / "second_correct.csv"

    path1.write_text("", encoding="utf-8")

    path2.write_text(
        "timestamp,level,source,message\n2026-10-23T13:00:00+03:00,INFO,auth,correct\n",
        encoding="utf-8",
    )

    skip_lines = {"skip_lines": 0}

    result = list(
        read_events([str(path1), str(path2)], skip_lines, ["jsonl", "csv"], True)
    )

    assert len(result) == 1
    assert skip_lines["skip_lines"] == 0

    assert result[0].message == "correct"
    assert "пустой файл" in caplog.text
    assert str(path1) in caplog.text


def test_some_files_incorrect_first_and_second_skip_invalid(tmp_path, caplog):
    path1 = tmp_path / "first_incorrect.jsonl"
    path2 = tmp_path / "second_incorrect.csv"

    path1.write_text(
        '{"incorrect"}\n'
        '{"timestamp":"2026-10-23T12:00:00+03:00",'
        '"level":"INFO",'
        '"source":"auth",'
        '"message":"first_correct"}\n',
        encoding="utf-8",
    )

    path2.write_text(
        "timestamp,level,source,message\n"
        "2026-10-23T13:00:00+03:00,ERROR,auth,incorrect,EXTRA\n"
        "2026-10-23T14:00:00+03:00,INFO,auth,second_correct\n",
        encoding="utf-8",
    )

    skip_lines = {"skip_lines": 0}

    result = list(
        read_events([str(path1), str(path2)], skip_lines, ["jsonl", "csv"], True)
    )

    assert len(result) == 2
    assert skip_lines["skip_lines"] == 2

    assert result[0].message == "first_correct"
    assert result[1].message == "second_correct"

    assert "пропущена строка 1" in caplog.text
    assert "пропущена строка 2" in caplog.text


def test_some_files_one_format(tmp_path):
    path1 = tmp_path / "file1.csv"
    path2 = tmp_path / "file2.csv"

    path1.write_text(
        "timestamp,level,source,message\n"
        "2026-10-23T12:00:00+03:00,INFO,auth,first csv file\n",
        encoding="utf-8",
    )

    path2.write_text(
        "timestamp,level,source,message\n"
        "2026-10-23T13:00:00+03:00,ERROR,auth,second csv file\n",
        encoding="utf-8",
    )

    skip_lines = {"skip_lines": 0}

    result = list(read_events([str(path1), str(path2)], skip_lines, ["csv"], False))

    assert len(result) == 2
    assert skip_lines["skip_lines"] == 0
    assert result[0].message == "first csv file"
    assert result[1].message == "second csv file"
