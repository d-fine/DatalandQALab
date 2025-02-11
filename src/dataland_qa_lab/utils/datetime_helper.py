from datetime import UTC, datetime, timedelta, timezone


def get_german_time_as_string() -> str:
    """Returns the current german time formatted as a string."""
    now_utc = datetime.now(UTC)
    ger_timezone = timedelta(hours=2) if now_utc.astimezone(timezone(timedelta(hours=1))).dst() else timedelta(hours=1)
    return (now_utc + ger_timezone).strftime("%Y-%m-%d %H:%M:%S")
