import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
from app.analytics.metrics import calculate_mae, calculate_rmse, calculate_bias


def compute_daily_accuracy(matched_df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Computes daily accuracy metrics from the matched records dataset.
    Grouped by local delivery date ('delivery_date').
    """
    if matched_df.empty:
        return []

    # Ensure required columns
    required_cols = {"delivery_date", "error", "forecast_mw", "actual_mw"}
    if not required_cols.issubset(matched_df.columns):
        raise ValueError(f"matched_df missing required columns for daily grouping: {required_cols - set(matched_df.columns)}")

    daily_results = []
    # Group by delivery_date ascending
    for date_str, group in matched_df.groupby("delivery_date", sort=True):
        errors = group["error"].values
        forecasts = group["forecast_mw"].values
        actuals = group["actual_mw"].values

        mae = calculate_mae(errors)
        rmse = calculate_rmse(errors)
        bias = calculate_bias(errors)
        max_err = round(float(np.max(np.abs(errors))), 2) if len(errors) > 0 else 0.0

        matched_count = len(group)
        # Expected intervals per day: standard UK delivery has 48 half-hour settlement periods
        expected_intervals = 48
        coverage_pct = round((matched_count / expected_intervals) * 100.0, 2)

        daily_results.append({
            "date": str(date_str),
            "mae_mw": mae,
            "rmse_mw": rmse,
            "bias_mw": bias,
            "max_error_mw": max_err,
            "mean_forecast_mw": round(float(np.mean(forecasts)), 2) if len(forecasts) > 0 else 0.0,
            "mean_actual_mw": round(float(np.mean(actuals)), 2) if len(actuals) > 0 else 0.0,
            "matched_intervals": matched_count,
            "expected_intervals": expected_intervals,
            "coverage_percent": coverage_pct,
        })

    return daily_results


def compute_error_distribution(matched_df: pd.DataFrame, num_bins: int = 12) -> Dict[str, Any]:
    """
    Computes histogram bins and frequency counts of forecast errors (MW).
    """
    if matched_df.empty:
        return {"bins": [], "total_samples": 0}

    errors = matched_df["error"].values
    counts, bin_edges = np.histogram(errors, bins=num_bins)

    bins_data = []
    for i in range(len(counts)):
        bin_min = round(float(bin_edges[i]), 1)
        bin_max = round(float(bin_edges[i + 1]), 1)
        bin_center = round((bin_min + bin_max) / 2.0, 1)
        label = f"{bin_min:+.0f} to {bin_max:+.0f} MW"

        bins_data.append({
            "bin_index": i,
            "label": label,
            "bin_min": bin_min,
            "bin_max": bin_max,
            "bin_center": bin_center,
            "count": int(counts[i]),
            "percentage": round(float(counts[i] / len(errors) * 100.0), 2),
        })

    return {
        "bins": bins_data,
        "total_samples": len(errors),
        "min_error_mw": round(float(np.min(errors)), 2),
        "max_error_mw": round(float(np.max(errors)), 2),
    }


def compute_extreme_errors(matched_df: pd.DataFrame, top_n: int = 10) -> List[Dict[str, Any]]:
    """
    Extracts intervals with the largest absolute forecast misses.
    """
    if matched_df.empty:
        return []

    df_copy = matched_df.copy()
    df_copy["abs_error"] = df_copy["error"].abs()
    top_extremes = df_copy.sort_values(by="abs_error", ascending=False).head(top_n)

    records = []
    for _, row in top_extremes.iterrows():
        records.append({
            "start_time_utc": row["start_time_utc"],
            "delivery_date": row["delivery_date"],
            "settlement_period": int(row.get("settlement_period", 0)) if pd.notna(row.get("settlement_period")) else None,
            "forecast_mw": round(float(row["forecast_mw"]), 2),
            "actual_mw": round(float(row["actual_mw"]), 2),
            "error_mw": round(float(row["error"]), 2),
            "abs_error_mw": round(float(row["abs_error"]), 2),
            "publish_time_utc": row.get("publish_time_utc"),
            "forecast_age_hours": round(float(row.get("forecast_age_hours", 0.0)), 1),
            "direction": "overforecast" if row["error"] > 0 else "underforecast",
        })

    return records
