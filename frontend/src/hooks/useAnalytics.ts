import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/client';

export interface TrendDataPoint {
  date: string;
  value: number;
  secondary_value?: number;
}

export interface RegionalCompareData {
  region_name: string;
  avg_compliance: number;
  total_incidents: number;
  avg_risk: number;
}

export function useSafetyTrends() {
  return useQuery({
    queryKey: ['analytics', 'trends', 'safety'],
    queryFn: async () => {
      const { data } = await apiClient.get<TrendDataPoint[]>('/api/v1/analytics/trends/safety');
      return data;
    },
  });
}

export function useRegionalCompare() {
  return useQuery({
    queryKey: ['analytics', 'compare', 'regions'],
    queryFn: async () => {
      const { data } = await apiClient.get<RegionalCompareData[]>('/api/v1/analytics/compare/regions');
      return data;
    },
  });
}
