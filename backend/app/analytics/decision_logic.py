from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from app.utils.datetime_utils import calculate_decision_cutoff_utc, UTC_TZ
from app.models.forecast import WindForecast


def get_decision_cutoff_for_interval(
    target_start_time_utc: datetime,
    cutoff_time_str: str = "10:00",
    tz_name: str = "Europe/London",
) -> datetime:
    """
    Computes the decision cutoff timestamp in UTC for a target delivery interval.
    Assumes decisions are made at 10:00 AM local UK time on the previous calendar day.
    """
    return calculate_decision_cutoff_utc(
        target_start_time_utc=target_start_time_utc,
        cutoff_time_str=cutoff_time_str,
        tz_name=tz_name,
    )


def is_forecast_eligible(
    publish_time_utc: datetime,
    cutoff_utc: datetime,
) -> bool:
    """
    Checks if a forecast publication timestamp is strictly before or at the decision cutoff.
    """
    if publish_time_utc.tzinfo is None:
        publish_time_utc = publish_time_utc.replace(tzinfo=UTC_TZ)
    if cutoff_utc.tzinfo is None:
        cutoff_utc = cutoff_utc.replace(tzinfo=UTC_TZ)
    return publish_time_utc <= cutoff_utc


def select_best_eligible_forecast(
    forecasts: List[WindForecast],
    cutoff_utc: datetime,
) -> Optional[WindForecast]:
    """
    Selects the latest eligible forecast published at or before cutoff_utc.
    If multiple forecasts share the exact latest publication timestamp, returns the first.
    If no eligible forecast exists, returns None.
    """
    eligible = [f for f in forecasts if is_forecast_eligible(f.publish_time_utc, cutoff_utc)]
    if not eligible:
        return None
    # Sort descending by publish_time_utc
    eligible.sort(key=lambda f: f.publish_time_utc, reverse=True)
    return eligible[0]
