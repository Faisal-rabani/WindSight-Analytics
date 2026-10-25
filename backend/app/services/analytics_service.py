from datetime import date
from typing import Dict, Any, Optional
from app.services.matching_service import MatchingService
from app.analytics.metrics import compute_metrics_summary
from app.analytics.aggregation import (
    compute_daily_accuracy,
    compute_error_distribution,
    compute_extreme_errors,
)


class AnalyticsService:
    """Service providing processed analytics and statistical metrics for API endpoints."""

    def __init__(self, matching_service: Optional[MatchingService] = None):
        self.matching_service = matching_service or MatchingService()

    def get_overview(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Provides high-level dashboard overview metrics and trend previews."""
        matched_df, meta = self.matching_service.match_range(start_date, end_date)

        summary = compute_metrics_summary(
            matched_df=matched_df,
            expected_intervals=meta["expected_intervals"],
            total_actuals_available=meta["available_actuals"],
        )

        daily = compute_daily_accuracy(matched_df)
        extremes = compute_extreme_errors(matched_df, top_n=5)

        return {
            "period": f"{start_date.strftime('%Y-%m')}",
            "start_date": str(start_date),
            "end_date": str(end_date),
            "decision_time": self.matching_service.cutoff_time_str,
            "timezone": self.matching_service.tz_name,
            "metrics": summary,
            "daily_trend_preview": daily,
            "top_misses_preview": extremes,
        }

    def get_daily_accuracy(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Provides daily MAE, RMSE, Bias, and coverage statistics."""
        matched_df, meta = self.matching_service.match_range(start_date, end_date)
        daily = compute_daily_accuracy(matched_df)
        return {
            "meta": meta,
            "days": daily,
        }

    def get_error_distribution(
        self, start_date: date, end_date: date, num_bins: int = 12
    ) -> Dict[str, Any]:
        """Provides histogram binning for forecast error distribution."""
        matched_df, meta = self.matching_service.match_range(start_date, end_date)
        dist = compute_error_distribution(matched_df, num_bins=num_bins)
        return {
            "meta": meta,
            **dist,
        }

    def get_extreme_errors(
        self, start_date: date, end_date: date, top_n: int = 15
    ) -> Dict[str, Any]:
        """Provides intervals with the largest forecast errors."""
        matched_df, meta = self.matching_service.match_range(start_date, end_date)
        extremes = compute_extreme_errors(matched_df, top_n=top_n)
        return {
            "meta": meta,
            "extremes": extremes,
        }

    def get_data_quality(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Provides completeness, missing records, and coverage metrics."""
        matched_df, meta = self.matching_service.match_range(start_date, end_date)
        matched_count = len(matched_df)
        expected = meta["expected_intervals"]
        coverage_pct = round((matched_count / expected) * 100.0, 2) if expected > 0 else 0.0

        return {
            "period": f"{start_date} to {end_date}",
            "expected_intervals": expected,
            "available_actual_intervals": meta["available_actuals"],
            "matched_intervals": matched_count,
            "missing_forecast_count": meta["missing_forecast_count"],
            "missing_actual_count": meta["missing_actual_count"],
            "coverage_percent": coverage_pct,
            "decision_cutoff_rule": f"Previous day at {self.matching_service.cutoff_time_str} {self.matching_service.tz_name}",
        }
