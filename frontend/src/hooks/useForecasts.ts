import { useQuery } from '@tanstack/react-query';
import { forecastService, ComparisonParams } from '../services/forecastService';

export function useForecastComparison(params: ComparisonParams = {}) {
  return useQuery({
    queryKey: ['forecast-comparison', params.start_date, params.end_date, params.page, params.per_page],
    queryFn: () => forecastService.getComparison(params),
    staleTime: 5 * 60 * 1000,
  });
}

export function useForecastTimeseries(start_date?: string, end_date?: string) {
  return useQuery({
    queryKey: ['forecast-timeseries', start_date, end_date],
    queryFn: () => forecastService.getTimeseries(start_date, end_date),
    staleTime: 5 * 60 * 1000,
  });
}
