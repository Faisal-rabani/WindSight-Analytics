import { useQuery } from '@tanstack/react-query';
import { analyticsService, DateFilterParams } from '../services/analyticsService';

export function useOverview(params: DateFilterParams = {}) {
  return useQuery({
    queryKey: ['overview', params.start_date, params.end_date],
    queryFn: () => analyticsService.getOverview(params),
    staleTime: 5 * 60 * 1000,
  });
}
