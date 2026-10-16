from datetime import datetime
from streamstats.errors import InvalidEventError, InvalidTimestampError
 

VALID_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")

class Event:
    def __init__(self,
                 timestamp: datetime,
                 level: str,
                 source: str,
                 message: str) -> None :
        
        if level not in VALID_LEVELS:
            raise InvalidEventError("недопустимый уровень события ")
    
        if not isinstance(timestamp, datetime):
            raise InvalidTimestampError("некорректная временная метка")
        
        if not isinstance(source, str):
            raise InvalidEventError("некорректный формат source")
        temp = source
        temp = temp.replace(' ', '')
        
        if temp == '':
            raise InvalidEventError("некорректный формат source")
        
        if not isinstance(message, str):
            raise InvalidEventError("некорректный формат message") 
        
        self.timestamp = timestamp
        self.level = level
        self.source = source
        self.message = message