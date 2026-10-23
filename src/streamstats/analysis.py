from streamstats.constants import LEVEL_PRIORITY, TOP_SOURCE_LIMIT


def analyze(events):
    '''анализирую данные каждого полученного события и получаю данные для report.py'''
    count_event = 0

    earliest_timestamp = None
    latest_timestamp = None

    level_counts = {
        "INFO": 0,
        "DEBUG": 0,
        "WARNING": 0,
        "ERROR": 0,
        "CRITICAL": 0,
    }

    source_counts = {}

    level_source_counts = {}

    for event in events:
        level_counts[event.level] += 1

        source = event.source
        source_counts[source] = source_counts.get(source, 0) + 1

        if event.level == "ERROR" or event.level == "CRITICAL":
            key = (source, event.level)
            level_source_counts[key] = level_source_counts.get(key, 0) + 1


        if count_event == 0:
            earliest_timestamp = event.timestamp
            latest_timestamp = event.timestamp

        latest_timestamp = max(latest_timestamp, event.timestamp)
        earliest_timestamp = min(earliest_timestamp, event.timestamp)

        count_event += 1

    top_5_source = sorted(
        level_source_counts.items(),
        key=lambda item: (item[1], LEVEL_PRIORITY),
        reverse=True,
    )[:TOP_SOURCE_LIMIT]

    return (
        count_event,
        level_counts,
        source_counts,
        level_source_counts,
        top_5_source,
        earliest_timestamp,
        latest_timestamp,
    )
