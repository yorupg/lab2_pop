from streamstats.parsers import parse_csv, parse_jsonl

"""юникод тесты писать для режима --skip-lines бессмысленно, тк если все нормально обрабатывается, то ошибка не появляется и пропускать нечего"""


def test_unicode_jsonl(tmp_path):
    path = tmp_path / "unicode.jsonl"

    path.write_text(
        '{"timestamp":"2026-10-23T12:00:00+03:00",'
        '"level":"INFO",'
        '"source":"авторизация",'
        '"message":"корректный файл"}\n',
        encoding="utf-8",
    )

    skip_lines = {"skip_lines": 0}

    result = list(parse_jsonl(path, skip_lines, False))

    assert len(result) == 1
    assert result[0].source == "авторизация"
    assert result[0].message == "корректный файл"
    assert skip_lines["skip_lines"] == 0


def test_unicode_csv(tmp_path):
    path = tmp_path / "unicode.csv"

    path.write_text(
        "timestamp,level,source,message\n"
        "2026-10-23T12:00:00+03:00,INFO,информация,корректный файл\n"
        "2026-10-23T13:00:00+03:00,ERROR,ошибка,корректный файл\n",
        encoding="utf-8",
    )

    skip_lines = {"skip_lines": 0}

    result = list(parse_csv(path, skip_lines, False))

    assert len(result) == 2
    assert skip_lines["skip_lines"] == 0

    assert result[0].source == "информация"
    assert result[0].message == "корректный файл"

    assert result[1].source == "ошибка"
    assert result[1].message == "корректный файл"
