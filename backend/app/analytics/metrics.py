import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Sequence


def calculate_forecast_error(forecast_mw: float, actual_mw: float) -> float:
    """
    Computes individual interval forecast error in MW.
    error = forecast_generation - actual_generation
    Positive error: overforecast (forecast > actual).
    Negative error: underforecast (forecast < actual).
    """
    return round(forecast_mw - actual_mw, 2)


def calculate_mae(errors: Sequence[float]) -> float:
    """
    Mean Absolute Error (MAE):
    MAE = mean(abs(error))
    Measures the average magnitude of errors in MW without considering direction.
    """
    if len(errors) == 0:
        return 0.0
    arr = np.array(errors, dtype=float)
    return round(float(np.mean(np.abs(arr))), 2)


def calculate_rmse(errors: Sequence[float]) -> float:
    """
    Root Mean Square Error (RMSE):
    RMSE = sqrt(mean(error^2))
    Penalizes larger forecast errors more heavily.
    """
    if len(errors) == 0:
        return 0.0
    arr = np.array(errors, dtype=float)
    return round(float(np.sqrt(np.mean(arr ** 2))), 2)


def calculate_bias(errors: Sequence[float]) -> float:
    """
    Mean Bias Error (MBE):
    MBE = mean(error)
    Positive bias indicates systematic overforecasting.
    Negative bias indicates systematic underforecasting.
    """
    if len(errors) == 0:
        return 0.0
    arr = np.array(errors, dtype=float)
    return round(float(np.mean(arr)), 2)


def compute_metrics_summary(
    matched_df: pd.DataFrame,
    expected_intervals: int = 0,
    total_actuals_available: int = 0,
) -> Dict[str, Any]:
    """
    Calculates the complete battery of statistical accuracy metrics from matched records.
    matched_df must contain columns: 'forecast_mw', 'actual_mw', 'error'.
    """
    matched_count = len(matched_df)

    if matched_count == 0:
        return {
            "mae_mw": 0.0,
            "rmse_mw": 0.0,
            "bias_mw": 0.0,
            "max_absolute_error_mw": 0.0,
            "min_forecast_mw": 0.0,
            "max_forecast_mw": 0.0,
            "mean_forecast_mw": 0.0,
            "mean_actual_mw": 0.0,
            "matched_intervals": 0,
            "expected_intervals": expected_intervals,
            "missing_forecast_count": max(0, expected_intervals - matched_count),
            "missing_actual_count": max(0, expected_intervals - total_actuals_available),
            "coverage_percent": 0.0,
        }

    errors = matched_df["error"].values
    forecasts = matched_df["forecast_mw"].values
    actuals = matched_df["actual_mw"].values

    mae = calculate_mae(errors)
    rmse = calculate_rmse(errors)
    bias = calculate_bias(errors)
    max_abs_err = round(float(np.max(np.abs(errors))), 2)

    min_forecast = round(float(np.min(forecasts)), 2)
    max_forecast = round(float(np.max(forecasts)), 2)
    mean_forecast = round(float(np.mean(forecasts)), 2)
    mean_actual = round(float(np.mean(actuals)), 2)

    denom = expected_intervals if expected_intervals > 0 else matched_count
    coverage_pct = round((matched_count / denom) * 100.0, 2) if denom > 0 else 0.0

    missing_forecasts = max(0, expected_intervals - matched_count)
    missing_actuals = max(0, expected_intervals - total_actuals_available)

    return {
        "mae_mw": mae,
        "rmse_mw": rmse,
        "bias_mw": bias,
        "max_absolute_error_mw": max_abs_err,
        "min_forecast_mw": min_forecast,
        "max_forecast_mw": max_forecast,
        "mean_forecast_mw": mean_forecast,
        "mean_actual_mw": mean_actual,
        "matched_intervals": matched_count,
        "expected_intervals": expected_intervals,
        "missing_forecast_count": missing_forecasts,
        "missing_actual_count": missing_actuals,
        "coverage_percent": coverage_pct,
    }
