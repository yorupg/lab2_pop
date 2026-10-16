import json
import csv
from typing import Iterator
from streamstats.models import Event
from datetime import datetime


def parse_json(path: str) -> Iterator[Event]:
    with open(path, encoding="utf-8") as file:
        for line in file:
            data = json.loads(line)
        
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
            event = Event(data["timestamp"], data["level"], data["source"], data["message"])
            
            yield event
            
def parse_csv(path: str) -> Iterator[Event]:
    with open(path, encoding="utf-8") as file:
       reader =  csv.DictReader(file)
       for data in reader:
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
            event = Event(data["timestamp"], data["level"], data["source"], data["message"])
                       
            yield event