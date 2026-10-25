export interface MatchedForecastItem {
  start_time_utc: string;
  delivery_date: string;
  settlement_period: number | null;
  forecast_mw: number;
  actual_mw: number;
  error: number;
  publish_time_utc: string;
  decision_cutoff_utc: string;
  forecast_age_hours: number;
}

export interface PaginationMeta {
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
  start_date?: string;
  end_date?: string;
}

export interface PaginatedResponse<T> {
  status: 'success' | 'error';
  data: T[];
  meta: PaginationMeta;
}

export interface ApiResponse<T> {
  status: 'success' | 'error';
  data: T;
  meta?: Record<string, any>;
  error?: {
    code: number;
    message: string;
    details?: any;
  };
}
