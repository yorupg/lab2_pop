class StreamStatsError(Exception):
    pass

class UnsupportedFormatError(StreamStatsError):
    pass

class InvalidEventError(StreamStatsError):
    pass

class InvalidTimestampError(StreamStatsError):
    pass

class CLIConfigError(StreamStatsError):
    pass
class InvalidLineError(StreamStatsError):
    
    def __init__(self, file_path: str, line_number: int, reason: str):
        
        self.file_path = file_path
        self.line_number = line_number
        self.reason = reason
        
        super().__init__(f"{file_path} {line_number} {reason}")