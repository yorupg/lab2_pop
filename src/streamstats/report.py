from streamstats.analysis import analyze


def report(events, skip_lines):
     (
        count_event,
        level_counts,
        source_counts,
        level_source_counts,
        top_5_source,
        earliest_timestamp,
        latest_timestamp,
    ) = analyze(events)
     
     report = {
    "count_event": count_event,
    "level_count": level_counts,
    "source_counts": source_counts,
    "level_source_counts": [ 
        {
            "source": source,
            "level": level,
            "count": count
        }
        for (source, level), count in level_source_counts.items()],
    "top_5_source": [ 
        {
            "source": source,
            "level": level,
            "count": count
        }
        for (source, level), count in top_5_source],
    "earliest_timestamp": earliest_timestamp.isoformat() if earliest_timestamp is not None else None,
    "latest_timestamp": latest_timestamp.isoformat() if latest_timestamp is not None else None,
    "skip_lines" : skip_lines["skip_lines"]
    }
    
     return report
