import pytest
from datetime import datetime, date, timezone
from app import create_app
from app.extensions import db
from app.models.actual import ActualGeneration
from app.models.forecast import WindForecast
from app.services.matching_service import MatchingService
from app.repositories.actual_repository import ActualRepository
from app.repositories.forecast_repository import ForecastRepository


@pytest.fixture
def app_with_test_db():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


def test_matching_exact_interval_and_cutoff(app_with_test_db):
    # Delivery on 2026-01-05 10:00 UTC
    st1 = datetime(2026, 1, 5, 10, 0, tzinfo=timezone.utc)
    # Decision cutoff is 2026-01-04 10:00 UTC

    # Insert actual
    act = ActualGeneration(
        start_time_utc=st1,
        fuel_type="WIND",
        generation_mw=8500.0,
        settlement_date="2026-01-05",
        settlement_period=21,
    )
    db.session.add(act)

    # Insert eligible forecast (Jan 4 09:30 UTC)
    fc_eligible = WindForecast(
        start_time_utc=st1,
        publish_time_utc=datetime(2026, 1, 4, 9, 30, tzinfo=timezone.utc),
        generation_mw=9000.0,
    )
    # Insert ineligible forecast published after cutoff (Jan 4 11:30 UTC)
    fc_ineligible = WindForecast(
        start_time_utc=st1,
        publish_time_utc=datetime(2026, 1, 4, 11, 30, tzinfo=timezone.utc),
        generation_mw=12000.0,
    )
    db.session.add_all([fc_eligible, fc_ineligible])
    db.session.commit()

    service = MatchingService()
    df, meta = service.match_range(start_date=date(2026, 1, 5), end_date=date(2026, 1, 5))

    assert len(df) == 1
    row = df.iloc[0]
    assert row["forecast_mw"] == 9000.0  # Selected eligible forecast, NOT 12000.0
    assert row["actual_mw"] == 8500.0
    assert row["error"] == 500.0
    assert meta["matched_intervals"] == 1


def test_idempotent_duplicate_handling(app_with_test_db):
    st = datetime(2026, 1, 10, 12, 0, tzinfo=timezone.utc)
    records = [
        {"start_time_utc": st, "fuel_type": "WIND", "generation_mw": 5000.0},
        {"start_time_utc": st, "fuel_type": "WIND", "generation_mw": 5000.0},
    ]
    added = ActualRepository.bulk_upsert(records)
    assert added == 1
    count = ActualRepository.get_count_in_range(st, st)
    assert count == 1
