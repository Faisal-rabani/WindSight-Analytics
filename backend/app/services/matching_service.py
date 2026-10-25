from datetime import datetime, date, time, timedelta, timezone
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict
import pandas as pd
from app.repositories.actual_repository import ActualRepository
from app.repositories.forecast_repository import ForecastRepository
from app.utils.datetime_utils import (
    calculate_decision_cutoff_utc,
    get_delivery_date_london,
    format_utc_iso,
    UTC_TZ,
    LONDON_TZ,
)
from app.utils.logger import get_logger

logger = get_logger("matching_service")

# Module-level cache shared across requests
_GLOBAL_MATCH_CACHE: Dict[str, Tuple[pd.DataFrame, Dict[str, Any]]] = {}


class MatchingService:
    """
    Coordinates decision-time forecast matching against actual generation.
    Applies the pilot assumption: previous-day 10:00 AM local time decision cutoff.
    Optimized with batch loading and module-level in-memory caching.
    """

    def __init__(self, cutoff_time_str: str = "10:00", tz_name: str = "Europe/London"):
        self.cutoff_time_str = cutoff_time_str
        self.tz_name = tz_name

    def match_range(
        self,
        start_date: date,
        end_date: date,
        fuel_type: str = "WIND",
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Matches actual wind generation records between start_date and end_date
        with the latest eligible wind forecast published at or before the previous-day
        10:00 AM decision cutoff.
        
        Returns:
            (matched_df, metadata_dict)
        """
        cache_key = f"{start_date}_{end_date}_{fuel_type}_{self.cutoff_time_str}_{self.tz_name}"
        if cache_key in _GLOBAL_MATCH_CACHE:
            df, meta = _GLOBAL_MATCH_CACHE[cache_key]
            return df.copy(), meta.copy()

        # Convert start_date and end_date to UTC boundary datetimes
        start_dt_utc = datetime.combine(start_date, time(0, 0), tzinfo=timezone.utc)
        end_dt_utc = datetime.combine(end_date, time(23, 59, 59), tzinfo=timezone.utc)

        # 1. Fetch all actual generation records in range (single query)
        actuals = ActualRepository.get_in_range(start_dt_utc, end_dt_utc, fuel_type=fuel_type)

        # 2. Fetch all wind forecasts targeting this delivery window in one bulk query
        forecasts = ForecastRepository.get_in_range(start_dt_utc, end_dt_utc)

        # Group forecasts by start_time_utc for O(1) interval lookup
        forecasts_by_start: Dict[datetime, List[Any]] = defaultdict(list)
        for fc in forecasts:
            st = fc.start_time_utc
            if st.tzinfo is None:
                st = st.replace(tzinfo=UTC_TZ)
            forecasts_by_start[st].append(fc)

        matched_rows = []
        missing_forecast_count = 0
        total_actual_intervals = len(actuals)

        # Expected intervals: number of days * 48 settlement periods
        num_days = (end_date - start_date).days + 1
        expected_intervals = num_days * 48

        for act in actuals:
            st = act.start_time_utc
            if st.tzinfo is None:
                st = st.replace(tzinfo=UTC_TZ)

            # Compute decision cutoff UTC for this interval
            cutoff_utc = calculate_decision_cutoff_utc(
                target_start_time_utc=st,
                cutoff_time_str=self.cutoff_time_str,
                tz_name=self.tz_name,
            )

            # Filter candidates published <= cutoff_utc
            candidates = forecasts_by_start.get(st, [])
            eligible = []
            for c in candidates:
                pub = c.publish_time_utc
                if pub.tzinfo is None:
                    pub = pub.replace(tzinfo=UTC_TZ)
                if pub <= cutoff_utc:
                    eligible.append((pub, c))

            deliv_date = get_delivery_date_london(st)

            if eligible:
                # Pick latest published eligible forecast
                eligible.sort(key=lambda x: x[0], reverse=True)
                pub_utc, best_fc = eligible[0]

                age_hours = round((st - pub_utc).total_seconds() / 3600.0, 1)
                forecast_mw = round(float(best_fc.generation_mw), 2)
                actual_mw = round(float(act.generation_mw), 2)
                error_mw = round(forecast_mw - actual_mw, 2)

                matched_rows.append({
                    "start_time_utc": format_utc_iso(st),
                    "delivery_date": str(deliv_date),
                    "settlement_period": act.settlement_period,
                    "forecast_mw": forecast_mw,
                    "actual_mw": actual_mw,
                    "error": error_mw,
                    "publish_time_utc": format_utc_iso(pub_utc),
                    "decision_cutoff_utc": format_utc_iso(cutoff_utc),
                    "forecast_age_hours": age_hours,
                })
            else:
                missing_forecast_count += 1

        matched_df = pd.DataFrame(matched_rows)

        metadata = {
            "start_date": str(start_date),
            "end_date": str(end_date),
            "cutoff_time": self.cutoff_time_str,
            "timezone": self.tz_name,
            "expected_intervals": expected_intervals,
            "available_actuals": total_actual_intervals,
            "matched_intervals": len(matched_rows),
            "missing_forecast_count": missing_forecast_count,
            "missing_actual_count": max(0, expected_intervals - total_actual_intervals),
        }

        _GLOBAL_MATCH_CACHE[cache_key] = (matched_df, metadata)
        return matched_df, metadata
