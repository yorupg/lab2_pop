from datetime import datetime

from streamstats.analysis import analyze
from streamstats.models import Event
from streamstats.report import report

print(analyze([]))

events = [
    Event(datetime(2025, 1, 3, 10, 0), "ERROR", "server", "Ошибка"),
    Event(datetime(2025, 1, 1, 9, 0), "INFO", "client", "Запуск"),
    Event(datetime(2025, 1, 5, 12, 0), "CRITICAL", "server", "Критическая ошибка"),
    Event(datetime(2025, 1, 2, 11, 0), "ERROR", "database", "Ошибка БД"),
]

print(analyze(events))

(
    count_event,
    level_counts,
    source_counts,
    level_source_counts,
    top_5_source,
    earliest_time,
    latest_time,
) = analyze(events)

print(count_event)
print(earliest_time)
print(latest_time)

report1 = {
    "count_event": count_event,
    "level_count": level_counts,
    "source_counts": source_counts,
    "level_source_counts": level_source_counts,
    "top_5_source": top_5_source,
    "earliest_time": earliest_time.isoformat(),
    "latest_time": latest_time.isoformat()
    
}

result = report(events)
print(result)

import json

result = report(events)

with open("report.json", "w", encoding="utf-8") as file:
    json.dump(result, file, ensure_ascii=False, indent=4)