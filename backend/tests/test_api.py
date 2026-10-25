import pytest
from datetime import datetime, timezone
from app import create_app
from app.extensions import db
from app.models.actual import ActualGeneration
from app.models.forecast import WindForecast


@pytest.fixture
def test_client():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        # Seed test data for 2026-01-02
        st = datetime(2026, 1, 2, 12, 0, tzinfo=timezone.utc)
        act = ActualGeneration(
            start_time_utc=st,
            fuel_type="WIND",
            generation_mw=11000.0,
            settlement_date="2026-01-02",
            settlement_period=25,
        )
        fc = WindForecast(
            start_time_utc=st,
            publish_time_utc=datetime(2026, 1, 1, 9, 30, tzinfo=timezone.utc),
            generation_mw=12500.0,
        )
        db.session.add_all([act, fc])
        db.session.commit()

        with app.test_client() as client:
            yield client

        db.session.remove()
        db.drop_all()


def test_health_endpoint(test_client):
    res = test_client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json["data"]
    assert data["status"] == "online"
    assert data["period"] == "2026-01"


def test_overview_endpoint(test_client):
    res = test_client.get("/api/v1/analytics/overview?start_date=2026-01-02&end_date=2026-01-02")
    assert res.status_code == 200
    data = res.json["data"]
    assert "metrics" in data
    assert data["metrics"]["matched_intervals"] == 1
    assert data["metrics"]["mae_mw"] == 1500.0


def test_forecast_comparison_endpoint(test_client):
    res = test_client.get("/api/v1/forecasts/comparison?start_date=2026-01-02&end_date=2026-01-02")
    assert res.status_code == 200
    json_data = res.json
    assert json_data["status"] == "success"
    assert len(json_data["data"]) == 1
    assert json_data["data"][0]["forecast_mw"] == 12500.0


def test_invalid_date_validation(test_client):
    # Invalid date string format
    res = test_client.get("/api/v1/analytics/overview?start_date=invalid-date")
    assert res.status_code == 400
    assert "Invalid start_date format" in res.json["error"]["message"]

    # Inverted date range
    res2 = test_client.get("/api/v1/analytics/overview?start_date=2026-01-10&end_date=2026-01-05")
    assert res2.status_code == 400
    assert "cannot be after end_date" in res2.json["error"]["message"]
