import pytest
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from app.utils.datetime_utils import (
    calculate_decision_cutoff_utc,
    get_delivery_date_london,
    parse_utc_timestamp,
    LONDON_TZ,
    UTC_TZ,
)
from app.models.forecast import WindForecast
from app.analytics.decision_logic import (
    is_forecast_eligible,
    select_best_eligible_forecast,
    get_decision_cutoff_for_interval,
)


def test_decision_cutoff_calculation():
    # Delivery target: 2026-01-15 14:00 UTC (GMT/UTC+0 in winter)
    target_st = datetime(2026, 1, 15, 14, 0, tzinfo=UTC_TZ)
    cutoff = calculate_decision_cutoff_utc(target_st, cutoff_time_str="10:00")
    # Previous calendar day 10:00 AM UTC
    expected = datetime(2026, 1, 14, 10, 0, tzinfo=UTC_TZ)
    assert cutoff == expected


def test_boundary_january_1_purchasing_decision():
    # Purchasing decision on Jan 1, 2026 10:00 AM is for delivery on Jan 2, 2026
    target_st = datetime(2026, 1, 2, 0, 0, tzinfo=UTC_TZ)
    cutoff = calculate_decision_cutoff_utc(target_st, cutoff_time_str="10:00")
    assert cutoff == datetime(2026, 1, 1, 10, 0, tzinfo=UTC_TZ)


def test_boundary_january_31_decision_february_1_delivery():
    # Purchasing decision on Jan 31, 2026 10:00 AM is for delivery on Feb 1, 2026
    target_st = datetime(2026, 2, 1, 18, 0, tzinfo=UTC_TZ)
    cutoff = calculate_decision_cutoff_utc(target_st, cutoff_time_str="10:00")
    assert cutoff == datetime(2026, 1, 31, 10, 0, tzinfo=UTC_TZ)


def test_forecast_eligibility():
    cutoff = datetime(2026, 1, 10, 10, 0, tzinfo=UTC_TZ)
    # Published before cutoff -> eligible
    assert is_forecast_eligible(datetime(2026, 1, 10, 9, 30, tzinfo=UTC_TZ), cutoff) is True
    # Published exactly at cutoff -> eligible
    assert is_forecast_eligible(datetime(2026, 1, 10, 10, 0, tzinfo=UTC_TZ), cutoff) is True
    # Published after cutoff -> strictly rejected
    assert is_forecast_eligible(datetime(2026, 1, 10, 10, 30, tzinfo=UTC_TZ), cutoff) is False
    assert is_forecast_eligible(datetime(2026, 1, 10, 11, 30, tzinfo=UTC_TZ), cutoff) is False


def test_select_best_eligible_forecast():
    target_st = datetime(2026, 1, 15, 12, 0, tzinfo=UTC_TZ)
    cutoff = datetime(2026, 1, 14, 10, 0, tzinfo=UTC_TZ)

    f1 = WindForecast(start_time_utc=target_st, publish_time_utc=datetime(2026, 1, 14, 4, 30, tzinfo=UTC_TZ), generation_mw=10000.0)
    f2 = WindForecast(start_time_utc=target_st, publish_time_utc=datetime(2026, 1, 14, 9, 30, tzinfo=UTC_TZ), generation_mw=12000.0)
    f3_post_cutoff = WindForecast(start_time_utc=target_st, publish_time_utc=datetime(2026, 1, 14, 11, 30, tzinfo=UTC_TZ), generation_mw=14000.0)

    # Should select f2 (09:30 is latest before 10:00 cutoff, f3 is rejected)
    selected = select_best_eligible_forecast([f1, f2, f3_post_cutoff], cutoff)
    assert selected is not None
    assert selected.publish_time_utc == datetime(2026, 1, 14, 9, 30, tzinfo=UTC_TZ)
    assert selected.generation_mw == 12000.0


def test_no_eligible_forecast_returns_none():
    target_st = datetime(2026, 1, 15, 12, 0, tzinfo=UTC_TZ)
    cutoff = datetime(2026, 1, 14, 10, 0, tzinfo=UTC_TZ)
    # Only forecasts after cutoff
    f_post = WindForecast(start_time_utc=target_st, publish_time_utc=datetime(2026, 1, 14, 15, 30, tzinfo=UTC_TZ), generation_mw=15000.0)
    selected = select_best_eligible_forecast([f_post], cutoff)
    assert selected is None
