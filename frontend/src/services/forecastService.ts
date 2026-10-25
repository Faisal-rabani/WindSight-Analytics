import { apiClient } from './apiClient';
import { MatchedForecastItem, PaginatedResponse, ApiResponse } from '../types/forecast';

export interface ComparisonParams {
  start_date?: string;
  end_date?: string;
  page?: number;
  per_page?: number;
}

export const forecastService = {
  async getComparison(params: ComparisonParams = {}): Promise<PaginatedResponse<MatchedForecastItem>> {
    const res = await apiClient.get<PaginatedResponse<MatchedForecastItem>>('/forecasts/comparison', {
      params,
    });
    return res.data;
  },

  async getTimeseries(start_date?: string, end_date?: string): Promise<MatchedForecastItem[]> {
    const res = await apiClient.get<ApiResponse<MatchedForecastItem[]>>('/forecasts/timeseries', {
      params: { start_date, end_date },
    });
    return res.data.data;
  },
};
