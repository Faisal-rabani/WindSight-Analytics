export interface MetricsSummary {
  mae_mw: number;
  rmse_mw: number;
  bias_mw: number;
  max_absolute_error_mw: number;
  min_forecast_mw: number;
  max_forecast_mw: number;
  mean_forecast_mw: number;
  mean_actual_mw: number;
  matched_intervals: number;
  expected_intervals: number;
  missing_forecast_count: number;
  missing_actual_count: number;
  coverage_percent: number;
}

export interface DailyAccuracyRecord {
  date: string;
  mae_mw: number;
  rmse_mw: number;
  bias_mw: number;
  max_error_mw: number;
  mean_forecast_mw: number;
  mean_actual_mw: number;
  matched_intervals: number;
  expected_intervals: number;
  coverage_percent: number;
}

export interface ErrorBin {
  bin_index: number;
  label: string;
  bin_min: number;
  bin_max: number;
  bin_center: number;
  count: number;
  percentage: number;
}

export interface ExtremeErrorRecord {
  start_time_utc: string;
  delivery_date: string;
  settlement_period: number | null;
  forecast_mw: number;
  actual_mw: number;
  error_mw: number;
  abs_error_mw: number;
  publish_time_utc: string;
  forecast_age_hours: number;
  direction: 'overforecast' | 'underforecast';
}

export interface OverviewData {
  period: string;
  start_date: string;
  end_date: string;
  decision_time: string;
  timezone: string;
  metrics: MetricsSummary;
  daily_trend_preview: DailyAccuracyRecord[];
  top_misses_preview: ExtremeErrorRecord[];
}

export interface DataQualityReport {
  period: string;
  expected_intervals: number;
  available_actual_intervals: number;
  matched_intervals: number;
  missing_forecast_count: number;
  missing_actual_count: number;
  coverage_percent: number;
  decision_cutoff_rule: string;
}
