from datetime import date
from typing import Dict, Any, Optional
from app.services.matching_service import MatchingService


class ForecastService:
    """Service providing wind forecast comparison data and details."""

    def __init__(self, matching_service: Optional[MatchingService] = None):
        self.matching_service = matching_service or MatchingService()

    def get_comparison(
        self,
        start_date: date,
        end_date: date,
        page: int = 1,
        per_page: int = 50,
    ) -> Dict[str, Any]:
        """
        Returns matched forecast vs actual records for the given date range,
        with pagination support and publication metadata.
        """
        matched_df, meta = self.matching_service.match_range(start_date, end_date)
        total_records = len(matched_df)

        if total_records == 0:
            return {
                "items": [],
                "total": 0,
                "meta": meta,
            }

        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_df = matched_df.iloc[start_idx:end_idx]

        items = page_df.to_dict(orient="records")

        return {
            "items": items,
            "total": total_records,
            "meta": meta,
        }

    def get_timeseries_all(
        self,
        start_date: date,
        end_date: date,
    ) -> Dict[str, Any]:
        """
        Returns unpaginated timeseries data for charting.
        """
        matched_df, meta = self.matching_service.match_range(start_date, end_date)
        items = matched_df.to_dict(orient="records") if not matched_df.empty else []
        return {
            "timeseries": items,
            "count": len(items),
            "meta": meta,
        }
