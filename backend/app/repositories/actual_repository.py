from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy import select, and_, func
from app.extensions import db
from app.models.actual import ActualGeneration


class ActualRepository:
    """Repository handling all database queries for ActualGeneration."""

    @staticmethod
    def get_by_start_time(start_time_utc: datetime, fuel_type: str = "WIND") -> Optional[ActualGeneration]:
        """Fetch a single actual record by start_time and fuel_type."""
        stmt = select(ActualGeneration).where(
            and_(
                ActualGeneration.start_time_utc == start_time_utc,
                ActualGeneration.fuel_type == fuel_type,
            )
        )
        return db.session.execute(stmt).scalar_one_or_none()

    @staticmethod
    def get_in_range(
        start_time_utc: datetime,
        end_time_utc: datetime,
        fuel_type: str = "WIND",
    ) -> List[ActualGeneration]:
        """Fetch all actual generation records within [start_time_utc, end_time_utc]."""
        stmt = (
            select(ActualGeneration)
            .where(
                and_(
                    ActualGeneration.start_time_utc >= start_time_utc,
                    ActualGeneration.start_time_utc <= end_time_utc,
                    ActualGeneration.fuel_type == fuel_type,
                )
            )
            .order_by(ActualGeneration.start_time_utc.asc())
        )
        return list(db.session.execute(stmt).scalars().all())

    @staticmethod
    def get_count_in_range(
        start_time_utc: datetime,
        end_time_utc: datetime,
        fuel_type: str = "WIND",
    ) -> int:
        """Count actual generation records within date range."""
        stmt = (
            select(func.count(ActualGeneration.id))
            .where(
                and_(
                    ActualGeneration.start_time_utc >= start_time_utc,
                    ActualGeneration.start_time_utc <= end_time_utc,
                    ActualGeneration.fuel_type == fuel_type,
                )
            )
        )
        return db.session.execute(stmt).scalar() or 0

    @staticmethod
    def bulk_upsert(records: List[dict]) -> int:
        """
        Inserts records, skipping existing ones (idempotent upsert).
        Returns number of newly added records.
        """
        if not records:
            return 0
        added_count = 0
        for r in records:
            existing = ActualRepository.get_by_start_time(
                r["start_time_utc"], r.get("fuel_type", "WIND")
            )
            if not existing:
                model = ActualGeneration(
                    start_time_utc=r["start_time_utc"],
                    fuel_type=r.get("fuel_type", "WIND"),
                    generation_mw=r["generation_mw"],
                    settlement_date=r.get("settlement_date"),
                    settlement_period=r.get("settlement_period"),
                )
                db.session.add(model)
                added_count += 1
            else:
                # Update generation if changed
                if existing.generation_mw != r["generation_mw"]:
                    existing.generation_mw = r["generation_mw"]
        db.session.commit()
        return added_count
