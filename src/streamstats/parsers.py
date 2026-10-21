import csv
import json
import logging
from collections.abc import Iterator

from pydantic import ValidationError

from streamstats.errors import (
    InvalidEventError,
    InvalidLineError,
    InvalidTimestampError,
)
from streamstats.models import Event


def validate_event(data):
    try:
        return Event.model_validate(data)
    
    except ValidationError as error:
        for problem in error.errors():
            if "timestamp" in  problem["loc"]:
                raise InvalidTimestampError(str(error)) from error
            
        raise InvalidEventError(str(error)) from error

def parse_jsonl(path: str, skip_lines: dict[str, int] ,skip_invalid: bool = False) -> Iterator[Event]:
    with open(path, encoding="utf-8") as file:
        for line_number, line in enumerate(file, start = 1):
            try:
                data = json.loads(line)
           
            except json.JSONDecodeError as error:
                
                if skip_invalid:
                    logging.warning(
                            "пропущена строка %s, файл: %s причина: %s",
                            line_number,
                            path,
                            error
                            )
                    skip_lines["skip_lines"] += 1
                    continue
                
                raise InvalidLineError(path, line_number, str(error)) from error
            
            try:
                event = validate_event(data)
                
            except (InvalidEventError, InvalidTimestampError) as error:
                
                if skip_invalid:
                    logging.warning(
                        "пропущена строка %s, файл: %s причина: %s",
                        line_number,
                        path,
                        error
                        )
                    skip_lines["skip_lines"] += 1
                    continue
                
                raise InvalidLineError(path, line_number, str(error)) from error
            
            yield event
            
def parse_csv(path: str, skip_lines: dict[str, int], skip_invalid: bool = False ) -> Iterator[Event]:
    with open(path, encoding="utf-8") as file:
        reader =  csv.DictReader(file)
       
        if reader.fieldnames is None:
           return
       
        required = ["timestamp", "level", "source", "message"]
       
        for name in required:
            if name not in reader.fieldnames:
                 raise InvalidLineError(path, 1, f"нет столбца {name}")        
       
        for data in reader:
            if None in data:
                reason = "лишние значения"
                if skip_invalid:
                    logging.warning(
                        "пропущена строка %s, файл: %s причина: %s",
                        reader.line_num,
                        path,
                        reason
                        )
                    skip_lines["skip_lines"] += 1
                    continue
                                
                raise InvalidLineError( path, reader.line_num, reason) 
                            
                
            try:
                event = validate_event(data)
            except (InvalidEventError, InvalidTimestampError) as error:
                
                if skip_invalid:
                    logging.warning(
                            "пропущена строка %s, файл: %s причина: %s",
                            reader.line_num,
                            path,
                            error
                            )                 
                    skip_lines["skip_lines"] += 1
                    continue
                
                raise InvalidLineError(path, reader.line_num, str(error)) from error
                       
            yield event