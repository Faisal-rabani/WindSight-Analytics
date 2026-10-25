import { useQuery } from '@tanstack/react-query';
import { analyticsService, DateFilterParams } from '../services/analyticsService';

export function useDailyAccuracy(params: DateFilterParams = {}) {
  return useQuery({
    queryKey: ['daily-accuracy', params.start_date, params.end_date],
    queryFn: () => analyticsService.getDailyAccuracy(params),
    staleTime: 5 * 60 * 1000,
  });
}

export function useErrorDistribution(params: DateFilterParams & { bins?: number } = {}) {
  return useQuery({
    queryKey: ['error-distribution', params.start_date, params.end_date, params.bins],
    queryFn: () => analyticsService.getErrorDistribution(params),
    staleTime: 5 * 60 * 1000,
  });
}

export function useExtremeErrors(params: DateFilterParams & { limit?: number } = {}) {
  return useQuery({
    queryKey: ['extreme-errors', params.start_date, params.end_date, params.limit],
    queryFn: () => analyticsService.getExtremes(params),
    staleTime: 5 * 60 * 1000,
  });
}

export function useDataQuality(params: DateFilterParams = {}) {
  return useQuery({
    queryKey: ['data-quality', params.start_date, params.end_date],
    queryFn: () => analyticsService.getDataQuality(params),
    staleTime: 5 * 60 * 1000,
  });
}
