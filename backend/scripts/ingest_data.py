import os
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app import create_app
from app.services.ingestion_service import IngestionService
from app.utils.logger import get_logger

logger = get_logger("cli_ingest")


def main():
    logger.info("Initializing application context for data ingestion...")
    app = create_app(os.getenv("FLASK_ENV", "development"))

    with app.app_context():
        service = IngestionService()
        logger.info("Starting January 2026 Elexon data ingestion...")
        summary = service.ingest_january_2026_scope()
        logger.info(f"Ingestion finished successfully: {summary}")
        print("\n=== Ingestion Completed Successfully ===")
        print(f"Actuals fetched: {summary['actuals']['total_fetched']} (added: {summary['actuals']['total_upserted']})")
        print(f"Forecasts fetched: {summary['forecasts']['total_fetched']} (added: {summary['forecasts']['total_upserted']})")


if __name__ == "__main__":
    main()
