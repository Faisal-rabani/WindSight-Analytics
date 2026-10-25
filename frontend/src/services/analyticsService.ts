import { apiClient } from './apiClient';
import {
  OverviewData,
  DailyAccuracyRecord,
  ErrorBin,
  ExtremeErrorRecord,
  DataQualityReport,
} from '../types/analytics';
import { ApiResponse } from '../types/forecast';

export interface DateFilterParams {
  start_date?: string;
  end_date?: string;
}

export const analyticsService = {
  async getOverview(params: DateFilterParams = {}): Promise<OverviewData> {
    const res = await apiClient.get<ApiResponse<OverviewData>>('/analytics/overview', {
      params,
    });
    return res.data.data;
  },

  async getDailyAccuracy(params: DateFilterParams = {}): Promise<DailyAccuracyRecord[]> {
    const res = await apiClient.get<ApiResponse<DailyAccuracyRecord[]>>('/analytics/daily', {
      params,
    });
    return res.data.data;
  },

  async getErrorDistribution(params: DateFilterParams & { bins?: number } = {}): Promise<ErrorBin[]> {
    const res = await apiClient.get<ApiResponse<ErrorBin[]>>('/analytics/distribution', {
      params,
    });
    return res.data.data;
  },

  async getExtremes(params: DateFilterParams & { limit?: number } = {}): Promise<ExtremeErrorRecord[]> {
    const res = await apiClient.get<ApiResponse<ExtremeErrorRecord[]>>('/analytics/extremes', {
      params,
    });
    return res.data.data;
  },

  async getDataQuality(params: DateFilterParams = {}): Promise<DataQualityReport> {
    const res = await apiClient.get<ApiResponse<DataQualityReport>>('/analytics/quality', {
      params,
    });
    return res.data.data;
  },
};
