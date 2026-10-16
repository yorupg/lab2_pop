

def analyze(events):
    count_event = 0
    
    level_counts = {
        "ERROR": 0,
        "WARNING": 0,
        "INFO": 0,
        "DEBUG": 0,
        "CRITICAL": 0,
    }
    
    source_counts = {}
    
    level_source_counts = {}
    
    for event in events:
        
        level_counts[event.level] += 1
        
        source = event.source 
        source_counts[source] = source_counts.get(source,0) + 1
        
        if event.level == "ERROR" or event.level == "CRITICAL":
            level_source_counts[source] = level_source_counts.get(source,0) + 1
        
        count_event += 1
        
    top_5_source = sorted(
        level_source_counts.items(),
        key = lambda item: item[1],
        reverse = True
        )[:5]
            
        
    return count_event, level_counts, source_counts, level_source_counts, top_5_source