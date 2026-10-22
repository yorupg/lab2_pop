from streamstats.parsers import parse_jsonl, parse_csv
from streamstats.errors import InvalidLineError, InvalidTimestampError, InvalidEventError
from datetime import timedelta
import pytest

'''тесты jsonl'''

def test_parser_jsonl_correct(tmp_path):
    path = tmp_path / "test_correct.jsonl"
    
    path.write_text(
        '{"timestamp":"2026-10-20T12:00:00+03:00",'
        '"level":"INFO",'
        '"source":"auth",'
        '"message":"correct file"}\n',
        
        encoding = "utf-8"
        
    )
    
    skip_lines = {"skip_lines": 0}
    
    result = list(parse_jsonl(path, skip_lines, False))
    
    assert len(result) == 1
    assert result[0].timestamp.isoformat() == "2026-10-20T12:00:00+03:00"
    assert result[0].timestamp.utcoffset() == timedelta(hours = 3)
    assert result[0].level == "INFO"
    assert result[0].source == "auth"   
    assert result[0].message == "correct file"
    assert skip_lines["skip_lines"] == 0

'''тесты jsonl'''

def test_parser_jsonl_incorrect_timestamp(tmp_path):
    path = tmp_path / "test_incorrect_timestamp.jsonl"
    
    path.write_text(
        '{"timestamp":"2026-10-20T12:00:00",'
        '"level":"INFO",'
        '"source":"auth",'
        '"message":"incorrect file"}\n',
        
        encoding = "utf-8"
        
    )
    
    skip_lines = {"skip_lines": 0}
    
    with pytest.raises(InvalidLineError) as error:
        list(parse_jsonl(path, skip_lines, False))
    
    assert isinstance(error.value.__cause__, InvalidTimestampError)
    assert error.value.line_number == 1
    assert skip_lines["skip_lines"] == 0

def test_parser_jsonl_incorrect_level(tmp_path):
    path = tmp_path / "test_incorrect_level.jsonl"
    
    path.write_text(
        '{"timestamp":"2026-10-20T12:00:00+03:00",'
        '"level":"INFO",'
        '"source":"auth",'
        '"message":"correct file"}\n'
        
        '{"timestamp":"2026-10-20T12:00:00+03:00",'
        '"level":"TEST",'
        '"source":"auth",'
        '"message":"incorrect file"}\n',
        
        encoding = "utf-8"
        
    )
    
    skip_lines = {"skip_lines": 0}
    
    with pytest.raises(InvalidLineError) as error:
        list(parse_jsonl(path, skip_lines, False))
    
    assert isinstance(error.value.__cause__, InvalidEventError)
    assert error.value.line_number == 2
    assert skip_lines["skip_lines"] == 0
    
def test_parser_jsonl_incorrect_skip_invalid(tmp_path, caplog):
    
    path = tmp_path / "test_incorrect_level.jsonl"
        
    path.write_text(
        '{"timestamp":"2026-10-20T12:00:00+03:00",'
        '"level":"INFO",'
        '"source":"auth",'
        '"message":"correct file line 1"}\n'
            
        '{"timestamp":"2026-10-20T12:00:00+08:00",'
        '"level":"TEST",'
        '"source":"auth",'
        '"message":"incorrect file line 2"}\n'
        
        '{"timestamp":"2026-10-20T12:00:00+07:00",'
        '"level":"INFO",'
        '"source":"auth",'
        '"message":"correct file line 3"}\n'
        
        '{"timestamp":"2026-10-20T12:00:00+06:00",'
        '"level":"INFO",'
        '"source":"         ",'
        '"message":"incorrect file line 4"}\n'
        
        '{"timestamp":"2026-10-20T12:00:00+01:00",'
        '"level":"INFO",'
        '"source":"auth",'
        '"message":"correct file line 5"}\n',  
           
        encoding = "utf-8"        
        )

    skip_lines = {"skip_lines": 0}
    
    result = list(parse_jsonl(path, skip_lines, True))
    
    assert len(result) == 3
    assert result[0].timestamp.isoformat() == "2026-10-20T12:00:00+03:00"
    assert result[0].timestamp.utcoffset() == timedelta(hours = 3)
    assert result[0].level == "INFO"
    assert result[0].source == "auth"   
    assert result[0].message == "correct file line 1"
    
    assert result[1].timestamp.isoformat() == "2026-10-20T12:00:00+07:00"
    assert result[1].timestamp.utcoffset() == timedelta(hours = 7)
    assert result[1].level == "INFO"
    assert result[1].source == "auth"   
    assert result[1].message == "correct file line 3"
    
    assert result[2].timestamp.isoformat() == "2026-10-20T12:00:00+01:00"
    assert result[2].timestamp.utcoffset() == timedelta(hours = 1)
    assert result[2].level == "INFO"
    assert result[2].source == "auth"   
    assert result[2].message == "correct file line 5"
    
    assert skip_lines["skip_lines"] == 2
    
    '''проверяю что были пропущены нужные строки'''
    assert "пропущена строка 2" in caplog.text
    assert "пропущена строка 4" in caplog.text
    
'''тесты csv'''

def test_parser_csv_correct(tmp_path):
    path = tmp_path / "test_correct.csv"
    
    path.write_text(
        "timestamp,level,source,message\n"
        "2026-10-20T12:00:00+03:00,INFO,auth,correct file\n",
        
        encoding = "utf-8"
        
    )
    
    skip_lines = {"skip_lines": 0}
    
    result = list(parse_csv(path, skip_lines, False))
    
    assert len(result) == 1
    assert result[0].timestamp.isoformat() == "2026-10-20T12:00:00+03:00"
    assert result[0].timestamp.utcoffset() == timedelta(hours = 3)
    assert result[0].level == "INFO"
    assert result[0].source == "auth"   
    assert result[0].message == "correct file"
    assert skip_lines["skip_lines"] == 0

def test_parser_csv_incorrect_timestamp(tmp_path):
    path = tmp_path / "test_incorrect_timestamp.csv"
    
    path.write_text(
        "timestamp,level,source,message\n"
        "2026-10-20T12:00:00,INFO,auth,incorrect file\n",
        
        encoding = "utf-8"
        
    )
    
    skip_lines = {"skip_lines": 0}
    
    with pytest.raises(InvalidLineError) as error:
        list(parse_csv(path, skip_lines, False))
    
    assert isinstance(error.value.__cause__, InvalidTimestampError)
    assert error.value.line_number == 2
    assert skip_lines["skip_lines"] == 0

def test_parser_csv_incorrect_level(tmp_path):
    path = tmp_path / "test_incorrect_level.csv"
    
    path.write_text(
        "timestamp,level,source,message\n"
        "2026-10-20T12:00:00+03:00,INFO,auth,correct file\n"
        "2026-10-20T12:00:00+03:00,TEST,auth,incorrect file\n",
        
        encoding = "utf-8"
        
    )
    
    skip_lines = {"skip_lines": 0}
    
    with pytest.raises(InvalidLineError) as error:
        list(parse_csv(path, skip_lines, False))
    
    assert isinstance(error.value.__cause__, InvalidEventError)
    assert error.value.line_number == 3
    assert skip_lines["skip_lines"] == 0
    
def test_parser_csv_incorrect_skip_invalid(tmp_path, caplog):
    
    path = tmp_path / "test_incorrect_level.csv"
        
    path.write_text(
        "timestamp,level,source,message\n"
        "2026-10-20T12:00:00+03:00,INFO,auth,correct file line 1\n"
        "2026-10-20T12:00:00+08:00,TEST,auth,incorrect file line 2\n"
        "2026-10-20T12:00:00+07:00,INFO,auth,correct file line 3\n"
        "2026-10-20T12:00:00+06:00,INFO,         ,incorrect file line 4\n"
        "2026-10-20T12:00:00+01:00,INFO,auth,correct file line 5\n", 
           
        encoding = "utf-8"        
        )

    skip_lines = {"skip_lines": 0}
    
    result = list(parse_csv(path, skip_lines, True))
    
    assert len(result) == 3
    assert result[0].timestamp.isoformat() == "2026-10-20T12:00:00+03:00"
    assert result[0].timestamp.utcoffset() == timedelta(hours = 3)
    assert result[0].level == "INFO"
    assert result[0].source == "auth"   
    assert result[0].message == "correct file line 1"
    
    assert result[1].timestamp.isoformat() == "2026-10-20T12:00:00+07:00"
    assert result[1].timestamp.utcoffset() == timedelta(hours = 7)
    assert result[1].level == "INFO"
    assert result[1].source == "auth"   
    assert result[1].message == "correct file line 3"
    
    assert result[2].timestamp.isoformat() == "2026-10-20T12:00:00+01:00"
    assert result[2].timestamp.utcoffset() == timedelta(hours = 1)
    assert result[2].level == "INFO"
    assert result[2].source == "auth"   
    assert result[2].message == "correct file line 5"
    
    assert skip_lines["skip_lines"] == 2
    
    '''проверяю что были пропущены нужные строки'''
    assert "пропущена строка 3" in caplog.text
    assert "пропущена строка 5" in caplog.text
    