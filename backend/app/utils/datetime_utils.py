from datetime import datetime, date, time, timedelta, timezone
from zoneinfo import ZoneInfo
from typing import Optional, Tuple


LONDON_TZ = ZoneInfo("Europe/London")
UTC_TZ = timezone.utc


def parse_utc_timestamp(ts_str: str) -> datetime:
    """
    Parses an ISO timestamp string into a timezone-aware UTC datetime.
    Handles 'Z' suffix, offsets, and microsecond variants.
    """
    if not ts_str:
        raise ValueError("Timestamp string cannot be empty")
    cleaned = ts_str.replace("Z", "+00:00")
    dt = datetime.fromisoformat(cleaned)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC_TZ)
    return dt.astimezone(UTC_TZ)


def format_utc_iso(dt: datetime) -> str:
    """Formats a datetime as UTC ISO 8601 string ending in 'Z'."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC_TZ)
    utc_dt = dt.astimezone(UTC_TZ)
    return utc_dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def get_delivery_date_london(start_time_utc: datetime) -> date:
    """
    Returns the calendar date of the delivery interval in the Europe/London timezone.
    """
    if start_time_utc.tzinfo is None:
        start_time_utc = start_time_utc.replace(tzinfo=UTC_TZ)
    london_dt = start_time_utc.astimezone(LONDON_TZ)
    return london_dt.date()


def calculate_decision_cutoff_utc(
    target_start_time_utc: datetime,
    cutoff_time_str: str = "10:00",
    tz_name: str = "Europe/London",
) -> datetime:
    """
    Calculates the decision cutoff timestamp in UTC for a target delivery interval.
    
    Pilot Assumption:
    Procurement decisions are made at 10:00 AM local time on the previous calendar day.
    
    Steps:
    1. Determine delivery date in Europe/London.
    2. Subtract one day to get previous calendar day.
    3. Construct 10:00 AM on that previous calendar day in Europe/London.
    4. Convert that local cutoff to UTC.
    """
    tz = ZoneInfo(tz_name)
    if target_start_time_utc.tzinfo is None:
        target_start_time_utc = target_start_time_utc.replace(tzinfo=UTC_TZ)
    
    local_delivery_dt = target_start_time_utc.astimezone(tz)
    delivery_date = local_delivery_dt.date()
    decision_date = delivery_date - timedelta(days=1)
    
    hour, minute = map(int, cutoff_time_str.split(":"))
    local_cutoff_dt = datetime.combine(decision_date, time(hour=hour, minute=minute), tzinfo=tz)
    return local_cutoff_dt.astimezone(UTC_TZ)


def get_settlement_period(start_time_utc: datetime) -> int:
    """
    Computes settlement period (1 to 48) for a UTC start time in Europe/London.
    Each period is 30 minutes. 00:00 to 00:30 is period 1.
    """
    if start_time_utc.tzinfo is None:
        start_time_utc = start_time_utc.replace(tzinfo=UTC_TZ)
    london_dt = start_time_utc.astimezone(LONDON_TZ)
    minutes = london_dt.hour * 60 + london_dt.minute
    return (minutes // 30) + 1
