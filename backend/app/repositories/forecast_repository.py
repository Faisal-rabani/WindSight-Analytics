from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy import select, and_, func
from app.extensions import db
from app.models.forecast import WindForecast


class ForecastRepository:
    """Repository handling all database queries for WindForecast."""

    @staticmethod
    def get_by_start_and_publish(
        start_time_utc: datetime, publish_time_utc: datetime
    ) -> Optional[WindForecast]:
        """Fetch a single forecast record by start_time and publish_time."""
        stmt = select(WindForecast).where(
            and_(
                WindForecast.start_time_utc == start_time_utc,
                WindForecast.publish_time_utc == publish_time_utc,
            )
        )
        return db.session.execute(stmt).scalar_one_or_none()

    @staticmethod
    def get_latest_forecast_before_cutoff(
        target_start_time_utc: datetime, cutoff_time_utc: datetime
    ) -> Optional[WindForecast]:
        """
        Finds the forecast for target_start_time_utc with the latest publish_time_utc
        satisfying publish_time_utc <= cutoff_time_utc.
        """
        stmt = (
            select(WindForecast)
            .where(
                and_(
                    WindForecast.start_time_utc == target_start_time_utc,
                    WindForecast.publish_time_utc <= cutoff_time_utc,
                )
            )
            .order_by(WindForecast.publish_time_utc.desc())
            .limit(1)
        )
        return db.session.execute(stmt).scalar_one_or_none()

    @staticmethod
    def get_all_for_start_times_before_cutoffs(
        target_start_times: List[datetime],
        cutoff_lookup: dict,
    ) -> List[WindForecast]:
        """
        Batch retrieval helper: given a list of target start times and a mapping of
        target_start_time -> cutoff_time_utc, returns the selected forecast for each.
        """
        selected = []
        for st in target_start_times:
            cutoff = cutoff_lookup.get(st)
            if cutoff:
                fc = ForecastRepository.get_latest_forecast_before_cutoff(st, cutoff)
                if fc:
                    selected.append(fc)
        return selected

    @staticmethod
    def get_in_range(
        start_time_utc: datetime, end_time_utc: datetime
    ) -> List[WindForecast]:
        """Fetch all wind forecasts for target delivery in [start_time_utc, end_time_utc]."""
        stmt = (
            select(WindForecast)
            .where(
                and_(
                    WindForecast.start_time_utc >= start_time_utc,
                    WindForecast.start_time_utc <= end_time_utc,
                )
            )
            .order_by(WindForecast.start_time_utc.asc(), WindForecast.publish_time_utc.asc())
        )
        return list(db.session.execute(stmt).scalars().all())

    @staticmethod
    def get_count_in_range(
        start_time_utc: datetime, end_time_utc: datetime
    ) -> int:
        """Count wind forecasts targeting delivery in [start_time_utc, end_time_utc]."""
        stmt = (
            select(func.count(WindForecast.id))
            .where(
                and_(
                    WindForecast.start_time_utc >= start_time_utc,
                    WindForecast.start_time_utc <= end_time_utc,
                )
            )
        )
        return db.session.execute(stmt).scalar() or 0

    @staticmethod
    def bulk_upsert(records: List[dict]) -> int:
        """
        Inserts forecast records, preserving all versions and skipping duplicates.
        Returns count of newly added records.
        """
        if not records:
            return 0
        added_count = 0
        for r in records:
            existing = ForecastRepository.get_by_start_and_publish(
                r["start_time_utc"], r["publish_time_utc"]
            )
            if not existing:
                model = WindForecast(
                    start_time_utc=r["start_time_utc"],
                    publish_time_utc=r["publish_time_utc"],
                    generation_mw=r["generation_mw"],
                )
                db.session.add(model)
                added_count += 1
            else:
                if existing.generation_mw != r["generation_mw"]:
                    existing.generation_mw = r["generation_mw"]
        db.session.commit()
        return added_count
