from datetime import date, datetime, timedelta, timezone
from typing import Dict, Any, Optional
from app.services.elexon_client import ElexonClient
from app.repositories.actual_repository import ActualRepository
from app.repositories.forecast_repository import ForecastRepository
from app.utils.logger import get_logger

logger = get_logger("ingestion_service")


class IngestionService:
    """Service orchestrating batch ingestion from Elexon API to local repositories."""

    def __init__(self, client: Optional[ElexonClient] = None):
        self.client = client or ElexonClient()

    def ingest_actual_generation(
        self,
        start_date: date,
        end_date: date,
        chunk_days: int = 7,
    ) -> Dict[str, Any]:
        """
        Ingests actual FUELHH wind generation records in chunks of `chunk_days`.
        """
        logger.info(f"Starting actual generation ingestion from {start_date} to {end_date}...")
        total_fetched = 0
        total_upserted = 0
        current_start = start_date

        while current_start <= end_date:
            current_end = min(current_start + timedelta(days=chunk_days - 1), end_date)
            logger.info(f"Ingesting actuals chunk: {current_start} to {current_end}")
            
            try:
                records = self.client.fetch_actual_generation(
                    settlement_date_from=current_start,
                    settlement_date_to=current_end,
                    fuel_type="WIND",
                )
                total_fetched += len(records)
                added = ActualRepository.bulk_upsert(records)
                total_upserted += added
                logger.info(f"Chunk {current_start}..{current_end}: {len(records)} fetched, {added} added")
            except Exception as e:
                logger.error(f"Failed to ingest actuals chunk {current_start}..{current_end}: {e}")
                raise

            current_start = current_end + timedelta(days=1)

        return {
            "dataset": "FUELHH",
            "fuel_type": "WIND",
            "start_date": str(start_date),
            "end_date": str(end_date),
            "total_fetched": total_fetched,
            "total_upserted": total_upserted,
        }

    def ingest_wind_forecasts(
        self,
        start_dt_utc: datetime,
        end_dt_utc: datetime,
        chunk_days: int = 5,
    ) -> Dict[str, Any]:
        """
        Ingests WINDFOR forecast records by publishDateTime in chunks of `chunk_days`.
        """
        logger.info(f"Starting forecast ingestion from {start_dt_utc} to {end_dt_utc}...")
        total_fetched = 0
        total_upserted = 0
        current_start = start_dt_utc

        while current_start < end_dt_utc:
            current_end = min(current_start + timedelta(days=chunk_days), end_dt_utc)
            logger.info(f"Ingesting forecasts chunk: {current_start} to {current_end}")

            try:
                records = self.client.fetch_wind_forecasts(
                    publish_from_utc=current_start,
                    publish_to_utc=current_end,
                )
                total_fetched += len(records)
                added = ForecastRepository.bulk_upsert(records)
                total_upserted += added
                logger.info(f"Chunk {current_start}..{current_end}: {len(records)} fetched, {added} added")
            except Exception as e:
                logger.error(f"Failed to ingest forecasts chunk {current_start}..{current_end}: {e}")
                raise

            current_start = current_end

        return {
            "dataset": "WINDFOR",
            "start_time": str(start_dt_utc),
            "end_time": str(end_dt_utc),
            "total_fetched": total_fetched,
            "total_upserted": total_upserted,
        }

    def ingest_january_2026_scope(self) -> Dict[str, Any]:
        """
        Convenience method to ingest the complete January 2026 analysis scope:
        - Actuals: 2026-01-01 to 2026-02-02 (covers decisions made through Jan 31).
        - Forecasts: 2025-12-30T00:00:00Z to 2026-02-01T23:59:59Z.
        """
        logger.info("Ingesting entire January 2026 pilot evaluation window...")
        actual_results = self.ingest_actual_generation(
            start_date=date(2026, 1, 1),
            end_date=date(2026, 2, 2),
        )
        forecast_results = self.ingest_wind_forecasts(
            start_dt_utc=datetime(2025, 12, 30, 0, 0, tzinfo=timezone.utc),
            end_dt_utc=datetime(2026, 2, 2, 0, 0, tzinfo=timezone.utc),
        )
        return {
            "status": "complete",
            "actuals": actual_results,
            "forecasts": forecast_results,
        }
