def filter_events_by_location(events, location):
    """Return events whose location contains `location` (case-insensitive)."""
    if not location:
        return list(events)
    needle = location.lower()
    return [e for e in events if needle in e.location.lower()]


def filter_events_by_title(events, title):
    """Return events whose title contains `title` (case-insensitive)."""
    if not title:
        return list(events)
    needle = title.lower()
    return [e for e in events if needle in e.title.lower()]