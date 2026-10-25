import pytest
import numpy as np
import pandas as pd
from app.analytics.metrics import (
    calculate_forecast_error,
    calculate_mae,
    calculate_rmse,
    calculate_bias,
    compute_metrics_summary,
)


def test_calculate_forecast_error():
    assert calculate_forecast_error(15000.0, 12000.0) == 3000.0
    assert calculate_forecast_error(10000.0, 14000.0) == -4000.0
    assert calculate_forecast_error(12500.5, 12500.5) == 0.0


def test_calculate_mae():
    errors = [100.0, -200.0, 300.0, -400.0]
    expected_mae = (100 + 200 + 300 + 400) / 4.0  # 250.0
    assert calculate_mae(errors) == expected_mae
    assert calculate_mae([]) == 0.0


def test_calculate_rmse():
    errors = [3.0, -4.0]
    # sqrt((9 + 16)/2) = sqrt(12.5) = 3.54
    assert calculate_rmse(errors) == 3.54
    assert calculate_rmse([]) == 0.0


def test_calculate_bias():
    # Positive bias = overforecast
    assert calculate_bias([100.0, 200.0, 300.0]) == 200.0
    # Negative bias = underforecast
    assert calculate_bias([-100.0, -200.0, -300.0]) == -200.0
    # Balanced
    assert calculate_bias([100.0, -100.0]) == 0.0
    assert calculate_bias([]) == 0.0


def test_compute_metrics_summary_empty():
    df_empty = pd.DataFrame(columns=["forecast_mw", "actual_mw", "error"])
    summary = compute_metrics_summary(df_empty, expected_intervals=48, total_actuals_available=48)
    assert summary["mae_mw"] == 0.0
    assert summary["rmse_mw"] == 0.0
    assert summary["bias_mw"] == 0.0
    assert summary["matched_intervals"] == 0
    assert summary["coverage_percent"] == 0.0
    assert summary["missing_forecast_count"] == 48


def test_compute_metrics_summary_with_data():
    df = pd.DataFrame({
        "forecast_mw": [10000.0, 12000.0, 15000.0],
        "actual_mw": [9000.0, 13000.0, 14000.0],
        "error": [1000.0, -1000.0, 1000.0],
    })
    summary = compute_metrics_summary(df, expected_intervals=6, total_actuals_available=6)
    assert summary["matched_intervals"] == 3
    assert summary["mae_mw"] == 1000.0
    assert summary["bias_mw"] == 333.33
    assert summary["min_forecast_mw"] == 10000.0
    assert summary["max_forecast_mw"] == 15000.0
    assert summary["mean_actual_mw"] == 12000.0
    assert summary["coverage_percent"] == 50.0
    assert summary["missing_forecast_count"] == 3
